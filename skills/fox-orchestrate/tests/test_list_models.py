"""Offline tests for scripts/list_models.py."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "list_models.py"
spec = importlib.util.spec_from_file_location("list_models", SCRIPT)
list_models = importlib.util.module_from_spec(spec)
sys.modules["list_models"] = list_models
spec.loader.exec_module(list_models)


def entry(slug: str, priority: int, visibility: str = "list", provider: str | None = None) -> dict:
    raw = {
        "slug": slug,
        "display_name": slug.upper(),
        "visibility": visibility,
        "priority": priority,
        "default_reasoning_level": "medium",
        "supported_reasoning_levels": [{"effort": "low"}, {"effort": "medium"}, {"effort": "high"}],
    }
    if provider is not None:
        raw["opencodex_capability_provenance"] = {"provider": provider}
    return raw


# Mirrors the observed runtime: five advertised overrides, three Claude models beyond the cap.
CATALOG = [
    entry("gpt-a", 0),
    entry("gpt-b", 1),
    entry("gpt-c", 2),
    entry("gpt-d", 3),
    entry("anthropic/fable", 4, provider="anthropic"),
    entry("anthropic/sonnet", 6, provider="anthropic"),
    entry("anthropic/opus", 5, provider="anthropic"),
    entry("anthropic/haiku", 7, provider="anthropic"),
    entry("gpt-old", 100, visibility="hide"),
]


class ListModelsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name).resolve()
        self.catalog = self.home / "catalog.json"
        self.catalog.write_text(json.dumps({"models": CATALOG}), encoding="utf-8")
        self.config = self.home / "config.toml"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write_config(self, text: str) -> None:
        self.config.write_text(text, encoding="utf-8")

    def run_main(self, *args: str, codex: bool = False) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        source = [] if codex else ["--no-codex"]
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = list_models.main(["--config", str(self.config), "--cwd", str(self.home), *source, *args])
        return code, out.getvalue(), err.getvalue()

    def run_json(self, *args: str, codex: bool = False) -> dict:
        code, out, err = self.run_main("--json", *args, codex=codex)
        self.assertEqual(code, 0, err)
        return json.loads(out)

    def fake_codex(self, models: list[dict], exit_code: int = 0) -> Path:
        """A stand-in for the Codex CLI that records its argv and prints a normalized catalog."""
        script = self.home / "fake-codex"
        argv_log = self.home / "argv.json"
        script.write_text(
            "#!/usr/bin/env python3\n"
            "import json, sys\n"
            f"if sys.argv[1:] == ['--version']:\n    print('codex-cli 9.9.9'); sys.exit(0)\n"
            f"import os\nopen({str(argv_log)!r}, 'w').write(json.dumps(sys.argv[1:]))\n"
            f"open({str(self.home / 'env.json')!r}, 'w').write(json.dumps(os.environ.get('CODEX_HOME')))\n"
            f"print({json.dumps(json.dumps({'models': models}))})\n"
            f"sys.exit({exit_code})\n",
            encoding="utf-8",
        )
        script.chmod(script.stat().st_mode | stat.S_IXUSR)
        return script

    def test_lists_every_visible_model_beyond_advertised_cap(self) -> None:
        self.write_config(f'model = "anthropic/opus"\nmodel_catalog_json = "{self.catalog}"\n')
        payload = self.run_json()
        slugs = [model["slug"] for model in payload["models"]]
        self.assertEqual(len(slugs), 8)
        self.assertNotIn("gpt-old", slugs)
        omitted = [model["slug"] for model in payload["models"] if not model["likely_advertised"]]
        self.assertEqual(omitted, ["anthropic/opus", "anthropic/sonnet", "anthropic/haiku"])
        self.assertEqual(payload["config_model"], "anthropic/opus")

    def test_provider_filter_uses_explicit_metadata_only(self) -> None:
        self.write_config(f'model_catalog_json = "{self.catalog}"\n')
        payload = self.run_json("--provider", "anthropic")
        self.assertEqual(
            [model["slug"] for model in payload["models"]],
            ["anthropic/fable", "anthropic/opus", "anthropic/sonnet", "anthropic/haiku"],
        )
        everything = self.run_json()
        self.assertIsNone(next(m for m in everything["models"] if m["slug"] == "gpt-a")["provider"])
        self.assertIn("4 entries have no provider metadata", payload["diagnostics"][0])

    def test_include_hidden_keeps_visibility(self) -> None:
        self.write_config(f'model_catalog_json = "{self.catalog}"\n')
        hidden = [m for m in self.run_json("--include-hidden")["models"] if m["slug"] == "gpt-old"]
        self.assertEqual(hidden[0]["visibility"], "hide")
        self.assertFalse(hidden[0]["likely_advertised"])

    def test_efforts_and_default_are_preserved(self) -> None:
        self.write_config(f'model_catalog_json = "{self.catalog}"\n')
        model = self.run_json()["models"][0]
        self.assertEqual(model["efforts"], ["low", "medium", "high"])
        self.assertEqual(model["default_effort"], "medium")

    def test_missing_effort_metadata_stays_unknown(self) -> None:
        raw = entry("bare", 0)
        del raw["supported_reasoning_levels"]
        self.catalog.write_text(json.dumps({"models": [raw]}), encoding="utf-8")
        self.write_config(f'model_catalog_json = "{self.catalog}"\n')
        self.assertIsNone(self.run_json()["models"][0]["efforts"])

    def test_missing_catalog_setting_reports_gap(self) -> None:
        self.write_config('model = "x"\n')
        code, _, err = self.run_main()
        self.assertEqual(code, 2)
        self.assertIn("model/list", err)

    def test_unknown_profile_and_bad_catalog_fail_clearly(self) -> None:
        self.write_config(f'model_catalog_json = "{self.catalog}"\n')
        code, _, err = self.run_main("--profile", "nope")
        self.assertEqual(code, 2)
        self.assertIn("profile not found", err)
        self.catalog.write_text("{not json", encoding="utf-8")
        code, _, err = self.run_main()
        self.assertEqual(code, 2)
        self.assertIn("not valid JSON", err)

    def test_table_states_omission_is_not_rejection(self) -> None:
        self.write_config(f'model_catalog_json = "{self.catalog}"\n')
        code, out, _ = self.run_main()
        self.assertEqual(code, 0)
        self.assertIn("anthropic/haiku", out)
        self.assertIn("likely omitted", out)
        self.assertIn("not rejection", out)

    def test_codex_source_is_preferred_and_receives_effective_catalog(self) -> None:
        # Codex normalizes entries and drops gateway provenance; providers come back from the file by slug.
        normalized = [{key: value for key, value in raw.items() if key != "opencodex_capability_provenance"}
                      for raw in CATALOG]
        fake = self.fake_codex(normalized)
        self.write_config(f'model_catalog_json = "{self.catalog}"\n')
        payload = self.run_json("--codex-bin", str(fake), "--provider", "anthropic", codex=True)
        self.assertEqual(payload["source"], "codex debug models")
        self.assertEqual(payload["codex_version"], "codex-cli 9.9.9")
        self.assertEqual(len(payload["models"]), 4)
        # Codex resolves the base config itself; the script must not override it.
        argv = json.loads((self.home / "argv.json").read_text(encoding="utf-8"))
        self.assertEqual(argv, ["debug", "models"])

    def test_profile_or_explicit_catalog_is_passed_to_codex(self) -> None:
        fake = self.fake_codex([entry("work-only", 0)])
        work = self.home / "work.json"
        self.write_config(f'model_catalog_json = "{self.catalog}"\n')
        (self.home / "work.config.toml").write_text('model_catalog_json = "work.json"\n', encoding="utf-8")
        self.run_json("--codex-bin", str(fake), "--profile", "work", codex=True)
        argv = json.loads((self.home / "argv.json").read_text(encoding="utf-8"))
        self.assertEqual(argv, ["debug", "models", "-c", f"model_catalog_json={json.dumps(str(work))}"])
        self.run_json("--codex-bin", str(fake), "--catalog", str(self.catalog), codex=True)
        argv = json.loads((self.home / "argv.json").read_text(encoding="utf-8"))
        self.assertEqual(argv[-1], f"model_catalog_json={json.dumps(str(self.catalog))}")

    def test_codex_can_list_models_without_a_catalog_file(self) -> None:
        fake = self.fake_codex([entry("builtin", 0)])
        self.write_config('model = "builtin"\n')
        payload = self.run_json("--codex-bin", str(fake), codex=True)
        self.assertEqual([m["slug"] for m in payload["models"]], ["builtin"])
        self.assertIsNone(payload["catalog_path"])
        argv = json.loads((self.home / "argv.json").read_text(encoding="utf-8"))
        self.assertEqual(argv, ["debug", "models"])

    def test_failed_codex_falls_back_to_file_with_diagnostic(self) -> None:
        fake = self.fake_codex([], exit_code=1)
        self.write_config(f'model_catalog_json = "{self.catalog}"\n')
        payload = self.run_json("--codex-bin", str(fake), codex=True)
        self.assertEqual(payload["source"], "catalog file")
        self.assertEqual(len(payload["models"]), 8)
        self.assertIn("exited 1", payload["diagnostics"][0])

    def test_missing_codex_and_catalog_reports_incomplete_inventory(self) -> None:
        self.write_config('model = "x"\n')
        code, _, err = self.run_main("--codex-bin", str(self.home / "missing"), codex=True)
        self.assertEqual(code, 2)
        self.assertIn("inventory is incomplete", err)

    def test_profile_file_layers_on_base_config(self) -> None:
        other = self.home / "catalogs" / "work.json"
        other.parent.mkdir()
        other.write_text(json.dumps([entry("work-only", 0)]), encoding="utf-8")
        self.write_config(f'model = "top"\nmodel_catalog_json = "{self.catalog}"\n')
        (self.home / "work.config.toml").write_text(
            'model = "work-model"\nmodel_catalog_json = "catalogs/work.json"\n', encoding="utf-8"
        )
        payload = self.run_json("--profile", "work")
        self.assertEqual([m["slug"] for m in payload["models"]], ["work-only"])
        self.assertEqual(payload["config_model"], "work-model")

    def test_codex_runs_against_the_config_home(self) -> None:
        fake = self.fake_codex([entry("home-model", 0)])
        self.write_config(f'model_catalog_json = "{self.catalog}"\n')
        self.run_json("--codex-bin", str(fake), codex=True)
        self.assertEqual(json.loads((self.home / "env.json").read_text(encoding="utf-8")), str(self.home))

    def test_missing_config_lets_codex_list_builtin_models(self) -> None:
        fake = self.fake_codex([entry("builtin", 0)])
        self.config.unlink(missing_ok=True)
        payload = self.run_json("--codex-bin", str(fake), codex=True)
        self.assertEqual([m["slug"] for m in payload["models"]], ["builtin"])

    def test_empty_inventory_is_an_error(self) -> None:
        self.catalog.write_text(json.dumps({"models": []}), encoding="utf-8")
        self.write_config(f'model_catalog_json = "{self.catalog}"\n')
        code, _, err = self.run_main()
        self.assertEqual(code, 2)
        self.assertIn("unknown, not empty", err)

    def test_provider_without_matches_names_present_providers(self) -> None:
        self.write_config(f'model_catalog_json = "{self.catalog}"\n')
        payload = self.run_json("--provider", "Anthropic")
        self.assertEqual(payload["models"], [])
        self.assertIn("providers present: anthropic", payload["diagnostics"][0])

    def test_version_mismatch_with_running_codex_is_reported(self) -> None:
        fake = self.fake_codex([entry("x", 0)])
        self.write_config(f'model_catalog_json = "{self.catalog}"\n')
        with mock.patch.dict(os.environ, {"CODEX_VERSION": "1.0.0"}):
            payload = self.run_json("--codex-bin", str(fake), codex=True)
        self.assertIn("running Codex is 1.0.0", payload["diagnostics"][0])
        with mock.patch.dict(os.environ, {"CODEX_VERSION": "9.9.9"}):
            payload = self.run_json("--codex-bin", str(fake), codex=True)
        self.assertEqual(payload["diagnostics"], [])

    def test_relative_config_with_other_cwd_keeps_the_config_home(self) -> None:
        fake = self.fake_codex([entry("home-model", 0)])
        self.write_config(f'model_catalog_json = "{self.catalog}"\n')
        elsewhere = self.home / "elsewhere"
        elsewhere.mkdir()
        relative = os.path.relpath(self.config, Path.cwd())
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = list_models.main(["--config", relative, "--cwd", str(elsewhere), "--codex-bin", str(fake), "--json"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads((self.home / "env.json").read_text(encoding="utf-8")), str(self.home.resolve()))

    def test_config_must_be_named_config_toml(self) -> None:
        other = self.home / "other.toml"
        other.write_text(f'model_catalog_json = "{self.catalog}"\n', encoding="utf-8")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = list_models.main(["--config", str(other), "--no-codex"])
        self.assertEqual(code, 2)
        self.assertIn("config.toml", err.getvalue())

    def test_no_visible_entries_is_explained(self) -> None:
        self.catalog.write_text(json.dumps({"models": [entry("only-hidden", 0, visibility="hide")]}), encoding="utf-8")
        self.write_config(f'model_catalog_json = "{self.catalog}"\n')
        payload = self.run_json()
        self.assertEqual(payload["models"], [])
        self.assertIn("none visible", payload["diagnostics"][0])

    def test_symlinked_config_keeps_its_home(self) -> None:
        store = self.home / "store"
        store.mkdir()
        (store / "codex-config.toml").write_text('model_catalog_json = "catalog.json"\n', encoding="utf-8")
        self.config.symlink_to(store / "codex-config.toml")
        fake = self.fake_codex([entry("home-model", 0)])
        payload = self.run_json("--codex-bin", str(fake), codex=True)
        self.assertEqual(payload["catalog_path"], str(self.catalog))
        self.assertEqual(json.loads((self.home / "env.json").read_text(encoding="utf-8")), str(self.home))


@unittest.skipUnless(shutil.which("codex"), "codex CLI not installed")
class RealCodexTest(unittest.TestCase):
    """Runs the real "codex debug models" against a temporary CODEX_HOME; offline, no model calls."""

    def test_lists_a_custom_catalog_through_real_codex(self) -> None:
        bundled = subprocess.run(
            ["codex", "debug", "models", "--bundled"], capture_output=True, text=True, timeout=60, check=True
        )
        template = json.loads(bundled.stdout)["models"][0]
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            models = []
            for index, slug in enumerate(["real-a", "real-b", "real-c", "real-d", "real-e", "real-f"]):
                model = dict(template, slug=slug, display_name=slug, visibility="list", priority=index)
                if index == 5:
                    model["opencodex_capability_provenance"] = {"provider": "anthropic"}
                models.append(model)
            catalog = home / "catalog.json"
            catalog.write_text(json.dumps({"models": models}), encoding="utf-8")
            (home / "config.toml").write_text(f'model_catalog_json = "{catalog}"\n', encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = list_models.main(["--config", str(home / "config.toml"), "--cwd", tmp, "--json"])
            self.assertEqual(code, 0)
            payload = json.loads(out.getvalue())
            self.assertEqual(payload["source"], "codex debug models")
            self.assertEqual([m["slug"] for m in payload["models"]], [m["slug"] for m in models])
            self.assertEqual(payload["models"][5]["provider"], "anthropic")
            self.assertFalse(payload["models"][5]["likely_advertised"])


if __name__ == "__main__":
    unittest.main()
