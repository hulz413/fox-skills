#!/usr/bin/env python3
"""List every model the target Codex runtime knows about before dispatch.

The spawn_agent tool description, and its unknown-model error, may name only the first few overrides,
so neither is an inventory. This script asks Codex itself for the effective catalog with
"codex debug models" (which applies Codex's own config resolution) and falls back to reading the
configured model_catalog_json file when the CLI is unavailable. It prints each entry's exact ID,
visibility, explicit provider, efforts and default. It does not call models or prove dispatch acceptance.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Codex advertises at most this many overrides in the spawn_agent description (model-discovery.md).
ADVERTISED_LIMIT = 5
CODEX_TIMEOUT_SECONDS = 60
SOURCE_CODEX = "codex debug models"
SOURCE_FILE = "catalog file"


class CatalogError(Exception):
    """The effective catalog cannot be resolved or read."""


@dataclass
class ModelEntry:
    slug: str
    display_name: str | None
    visibility: str | None
    priority: int | None
    provider: str | None
    efforts: list[str] | None
    default_effort: str | None
    likely_advertised: bool


@dataclass
class Settings:
    model: str | None
    catalog_path: Path | None
    # Set only when a profile chose the catalog; Codex resolves the base config itself.
    override_catalog: Path | None = None


@dataclass
class Request:
    config_path: Path
    profile: str | None
    catalog: Path | None
    codex_bin: str | None
    cwd: Path


@dataclass
class Inventory:
    source: str
    config_path: str
    profile: str | None
    catalog_path: str | None
    config_model: str | None
    models: list[ModelEntry]
    codex_version: str | None = None
    diagnostics: list[str] = field(default_factory=list)


def default_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")


def load_toml(path: Path) -> dict:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise CatalogError(f"config is not valid TOML: {path}: {exc}") from exc


def catalog_from(layer: dict, layer_path: Path) -> Path | None:
    value = layer.get("model_catalog_json")
    if not value:
        return None
    path = Path(os.path.expanduser(value))
    return path if path.is_absolute() else layer_path.parent / path


def resolve_settings(config_path: Path, profile: str | None) -> tuple[Settings, str | None]:
    """Apply the base config, then an explicit profile file <home>/<name>.config.toml.

    Codex no longer loads a legacy profile key or [profiles.<name>] table, so neither is emulated.
    A missing base config is empty: Codex then lists its built-in models.
    """
    base = load_toml(config_path) if config_path.is_file() else {}
    settings = Settings(model=base.get("model"), catalog_path=catalog_from(base, config_path))
    if profile is None:
        return settings, None
    profile_file = config_path.parent / f"{profile}.config.toml"
    if not profile_file.is_file():
        raise CatalogError(f"profile not found: {profile_file}")
    layer = load_toml(profile_file)
    settings.model = layer.get("model", settings.model)
    layer_catalog = catalog_from(layer, profile_file)
    if layer_catalog is not None:
        settings.catalog_path = settings.override_catalog = layer_catalog
    return settings, profile


def entries_from_json(text: str, origin: str) -> list[dict]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CatalogError(f"{origin} is not valid JSON: {exc}") from exc
    entries = data.get("models") if isinstance(data, dict) else data
    if not isinstance(entries, list):
        raise CatalogError(f"{origin} has no model list")
    return [entry for entry in entries if isinstance(entry, dict) and entry.get("slug")]


def read_catalog_file(catalog_path: Path) -> list[dict]:
    if not catalog_path.is_file():
        raise CatalogError(f"catalog not found: {catalog_path}")
    return entries_from_json(catalog_path.read_text(encoding="utf-8"), f"catalog {catalog_path}")


def codex_command(codex_bin: str, catalog_path: Path | None) -> list[str]:
    command = [codex_bin, "debug", "models"]
    if catalog_path is not None:
        # json.dumps yields a valid TOML basic string, so paths with spaces or quotes survive.
        command += ["-c", f"model_catalog_json={json.dumps(str(catalog_path))}"]
    return command


def codex_env(codex_home: Path) -> dict[str, str]:
    """Point Codex at the same home the script read, so --config cannot list another home's models."""
    return {**os.environ, "CODEX_HOME": str(codex_home)}


def read_codex_models(codex_bin: str, catalog_path: Path | None, cwd: Path, codex_home: Path) -> list[dict]:
    command = codex_command(codex_bin, catalog_path)
    try:
        result = subprocess.run(
            command, cwd=cwd, env=codex_env(codex_home), capture_output=True, text=True,
            timeout=CODEX_TIMEOUT_SECONDS, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CatalogError(f"{SOURCE_CODEX} could not run: {exc}") from exc
    if result.returncode != 0:
        detail = (result.stderr.strip().splitlines() or ["no stderr"])[-1]
        raise CatalogError(f"{SOURCE_CODEX} exited {result.returncode}: {detail}")
    return entries_from_json(result.stdout, SOURCE_CODEX)


def read_codex_version(codex_bin: str, codex_home: Path) -> str | None:
    """The desktop App may bundle a different Codex than the one on PATH; show which one answered."""
    try:
        result = subprocess.run(
            [codex_bin, "--version"], env=codex_env(codex_home), capture_output=True, text=True, timeout=10, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    lines = result.stdout.strip().splitlines()
    return lines[-1] if result.returncode == 0 and lines else None


def version_note(codex_version: str | None) -> str | None:
    """Codex exports CODEX_VERSION to commands it runs; a different CLI may resolve a different catalog."""
    runtime = os.environ.get("CODEX_VERSION")
    if not runtime or not codex_version or runtime in codex_version:
        return None
    return f"the running Codex is {runtime} but {codex_version} answered; pass --codex-bin for the runtime's binary"


def entry_efforts(raw: dict) -> list[str] | None:
    levels = raw.get("supported_reasoning_levels")
    if levels is None:
        return None
    return [level["effort"] if isinstance(level, dict) else str(level) for level in levels]


def entry_provider(raw: dict) -> str | None:
    """Only explicit metadata counts; a name or ID prefix is not provider evidence."""
    provenance = raw.get("opencodex_capability_provenance")
    if isinstance(provenance, dict) and provenance.get("provider"):
        return provenance["provider"]
    return raw.get("provider")


def sort_key(raw: dict) -> tuple[int, str]:
    priority = raw.get("priority")
    return (priority if isinstance(priority, int) else sys.maxsize, raw["slug"])


def file_providers(catalog_path: Path | None, diagnostics: list[str]) -> dict[str, str]:
    """Codex drops gateway fields such as opencodex_capability_provenance, so read providers from the file."""
    if catalog_path is None:
        return {}
    try:
        entries = read_catalog_file(catalog_path)
    except CatalogError as exc:
        diagnostics.append(f"provider metadata unavailable: {exc}")
        return {}
    return {raw["slug"]: provider for raw in entries if (provider := entry_provider(raw))}


def build_entries(raw_entries: list[dict], providers: dict[str, str]) -> list[ModelEntry]:
    ordered = sorted(raw_entries, key=sort_key)
    visible = [raw["slug"] for raw in ordered if raw.get("visibility") == "list"]
    advertised = set(visible[:ADVERTISED_LIMIT])
    return [
        ModelEntry(
            slug=raw["slug"],
            display_name=raw.get("display_name"),
            visibility=raw.get("visibility"),
            priority=raw.get("priority"),
            provider=entry_provider(raw) or providers.get(raw["slug"]),
            efforts=entry_efforts(raw),
            default_effort=raw.get("default_reasoning_level"),
            likely_advertised=raw["slug"] in advertised,
        )
        for raw in ordered
    ]


def build_inventory(request: Request) -> Inventory:
    settings, profile = resolve_settings(request.config_path, request.profile)
    catalog_path = request.catalog or settings.catalog_path
    diagnostics: list[str] = []
    raw_entries: list[dict] | None = None
    source = SOURCE_FILE
    codex_version = None
    if request.codex_bin is not None:
        codex_home = request.config_path.parent
        try:
            override = request.catalog or settings.override_catalog
            raw_entries = read_codex_models(request.codex_bin, override, request.cwd, codex_home)
            source = SOURCE_CODEX
            codex_version = read_codex_version(request.codex_bin, codex_home)
            if note := version_note(codex_version):
                diagnostics.append(note)
        except CatalogError as exc:
            diagnostics.append(str(exc))
    if raw_entries is None:
        if catalog_path is None:
            raise CatalogError(
                "codex CLI unavailable and no model_catalog_json is configured; the inventory is incomplete. "
                "Pass --codex-bin with the runtime's Codex binary, or query its model/list interface. "
                + " ".join(diagnostics)
            )
        raw_entries = read_catalog_file(catalog_path)
    if not raw_entries:
        detail = " ".join(diagnostics)
        raise CatalogError(f"{source} returned no models; the inventory is unknown, not empty. {detail}")
    providers = file_providers(catalog_path, diagnostics) if source == SOURCE_CODEX else {}
    return Inventory(
        source=source,
        config_path=str(request.config_path),
        profile=profile,
        catalog_path=str(catalog_path) if catalog_path else None,
        config_model=settings.model,
        models=build_entries(raw_entries, providers),
        codex_version=codex_version,
        diagnostics=diagnostics,
    )


def select_models(
    models: list[ModelEntry], provider: str | None, include_hidden: bool
) -> tuple[list[ModelEntry], str | None]:
    """Return the selection and a note when a provider filter could hide models."""
    selected = [model for model in models if include_hidden or model.visibility == "list"]
    if provider is None:
        hidden = None if selected else f"{len(models)} entries, none visible; pass --include-hidden"
        return selected, hidden
    matched = [model for model in selected if model.provider == provider]
    unknown = sum(1 for model in selected if model.provider is None)
    known = sorted({model.provider for model in selected if model.provider})
    notes = []
    if not matched:
        notes.append(f"no entry has provider {provider!r}; providers present: {', '.join(known) or 'none'}")
    if unknown:
        notes.append(
            f"{unknown} entries have no provider metadata and were excluded; their provider is unknown, not different"
        )
    return matched, "; ".join(notes) or None


def format_table(inventory: Inventory, models: list[ModelEntry]) -> str:
    if inventory.source == SOURCE_CODEX:
        catalog = f" (provider metadata from {inventory.catalog_path})" if inventory.catalog_path else ""
    else:
        catalog = f" ({inventory.catalog_path})"
    version = f" [{inventory.codex_version}]" if inventory.codex_version else ""
    lines = [
        f"source: {inventory.source}{version}{catalog}",
        f"config default model: {inventory.config_model or 'unknown'}",
    ]
    lines += [f"note: {message}" for message in inventory.diagnostics]
    lines.append("slug | display | visibility | provider | efforts (default) | in spawn_agent description")
    for model in models:
        efforts = ",".join(model.efforts) if model.efforts is not None else "unknown"
        lines.append(
            f"{model.slug} | {model.display_name or '-'} | {model.visibility or 'unknown'} | "
            f"{model.provider or 'unknown'} | {efforts} ({model.default_effort or 'unknown'}) | "
            f"{'likely' if model.likely_advertised else 'likely omitted'}"
        )
    lines.append(
        f"Omitted from the spawn_agent description or its error message is not rejection: Codex lists only "
        f"the first {ADVERTISED_LIMIT} visible overrides. Dispatch acceptance is still unverified."
    )
    return "\n".join(lines)


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", type=Path, help="Codex config.toml (default: $CODEX_HOME/config.toml)")
    parser.add_argument("--profile", help="profile file <name>.config.toml layered on the base config")
    parser.add_argument("--catalog", type=Path, help="use this catalog instead of the configured one")
    parser.add_argument("--codex-bin", default="codex", help="Codex CLI used for 'debug models' (default: codex)")
    parser.add_argument("--no-codex", action="store_true", help="read the catalog file without asking the Codex CLI")
    parser.add_argument(
        "--cwd", type=Path, default=Path.cwd(), help="task working directory, so a trusted project's config applies"
    )
    parser.add_argument("--provider", help="keep only models whose explicit provider matches, e.g. anthropic")
    parser.add_argument("--include-hidden", action="store_true", help="also list hidden entries")
    parser.add_argument("--json", action="store_true", help="print JSON instead of a table")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    # Absolute without following symlinks: Codex reads <home>/config.toml through a link in place.
    config_path = Path(os.path.abspath(args.config or default_codex_home() / "config.toml"))
    if config_path.name != "config.toml":
        print("error: --config must be a Codex home's config.toml; Codex reads no other file name", file=sys.stderr)
        return 2
    request = Request(
        config_path=config_path,
        profile=args.profile,
        catalog=args.catalog,
        codex_bin=None if args.no_codex else args.codex_bin,
        cwd=args.cwd,
    )
    try:
        inventory = build_inventory(request)
    except CatalogError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    models, note = select_models(inventory.models, args.provider, args.include_hidden)
    if note:
        inventory.diagnostics.append(note)
    if args.json:
        payload = asdict(inventory)
        payload["models"] = [asdict(model) for model in models]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(format_table(inventory, models))
    return 0


if __name__ == "__main__":
    sys.exit(main())
