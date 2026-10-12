#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

RUNTIME_ROOT = Path.cwd() / 'output' / 'anki-leetcode'
HIDDEN_RUNTIME = RUNTIME_ROOT / '.fox-anki'
VENV_ROOT = HIDDEN_RUNTIME / '.venv'
VENV_PYTHON = VENV_ROOT / 'bin' / 'python'
VENV_CLI = VENV_ROOT / 'bin' / 'fox-anki'
BOOTSTRAP_STATE = RUNTIME_ROOT / '.bootstrap-state.json'
FOX_ANKI_REPO_PATH_ENV = 'FOX_ANKI_REPO_PATH'
FOX_ANKI_REPO_URL = 'https://github.com/hulz413/fox-anki'

PRESERVED_NAMES = {'.venv', '.DS_Store'}
IGNORED_PARTS = {'.git', '.venv', '__pycache__', '.mypy_cache', '.pytest_cache', '.ruff_cache'}
IGNORED_NAMES = {'.DS_Store'}
IGNORED_DIR_NAMES = {'build', 'dist'}
DEPENDENCY_SPECS = ['anki==25.9.2', 'PyYAML', 'Pygments']
RUNTIME_REQUIRED_PATHS = [
    Path('pyproject.toml'),
    Path('README.md'),
    Path('LICENSE'),
    Path('src/fox_anki/__init__.py'),
    Path('src/fox_anki/cli.py'),
    Path('src/fox_anki/services/import_export.py'),
]


@dataclass(slots=True)
class SourceSpec:
    mode: str
    repo: str
    ref: str
    revision: str
    fingerprint: str | None
    source_path: Path | None = None



def run(cmd: list[str]) -> None:
    print('+', ' '.join(cmd))
    subprocess.run(cmd, check=True)



def should_ignore_path(path: Path, root: Path) -> bool:
    relative_parts = path.relative_to(root).parts
    if any(part in IGNORED_PARTS for part in relative_parts):
        return True
    if any(part in IGNORED_DIR_NAMES for part in relative_parts):
        return True
    if path.name in IGNORED_NAMES or path.suffix == '.pyc':
        return True
    return False



def iter_source_files(root: Path):
    for path in sorted(root.rglob('*')):
        if not path.is_file():
            continue
        if should_ignore_path(path, root):
            continue
        yield path



def compute_source_fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for path in iter_source_files(root):
        digest.update(str(path.relative_to(root)).encode('utf-8'))
        digest.update(b'\0')
        digest.update(path.read_bytes())
        digest.update(b'\0')
    return digest.hexdigest()



def resolve_python(candidate: str) -> Path | None:
    resolved = shutil.which(candidate)
    if resolved:
        return Path(resolved).resolve()

    candidate_path = Path(candidate).expanduser()
    if candidate_path.exists():
        return candidate_path.resolve()

    return None



def select_bootstrap_python() -> Path:
    candidates: list[str] = []
    env_python = os.environ.get('FOX_ANKI_BOOTSTRAP_PYTHON')
    if env_python:
        candidates.append(env_python)
    candidates.extend(['python3.11', str(Path(sys.executable).resolve())])

    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        resolved = resolve_python(candidate)
        if resolved is None:
            continue
        try:
            subprocess.run(
                [str(resolved), '--version'],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            continue
        return resolved

    raise RuntimeError('Unable to find a usable Python interpreter for fox-anki bootstrap.')



def validate_source_path(path: Path) -> Path:
    if not path.exists():
        raise RuntimeError(f'fox-anki source path does not exist: {path}')
    if not path.is_dir():
        raise RuntimeError(f'fox-anki source path must be a directory: {path}')
    if path.resolve() == HIDDEN_RUNTIME.resolve():
        raise RuntimeError('FOX_ANKI_REPO_PATH must not point at the hidden runtime directory.')

    missing = [str(required) for required in RUNTIME_REQUIRED_PATHS if not (path / required).exists()]
    if missing:
        raise RuntimeError(
            'fox-anki source is missing required files: ' + ', '.join(missing)
        )
    return path



def git_head_revision(path: Path) -> str:
    if shutil.which('git') is None:
        return ''
    result = subprocess.run(
        ['git', '-C', str(path), 'rev-parse', 'HEAD'],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ''
    return result.stdout.strip()



def parse_tag_sort_key(tag: str) -> tuple[int, int, int, int, str]:
    cleaned = tag[1:] if tag.startswith('v') else tag
    parts = cleaned.split('.')
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        return (0, 0, 0, 0, tag)
    major, minor, patch = (int(part) for part in parts)
    return (1, major, minor, patch, tag)



def resolve_latest_remote_tag() -> tuple[str, str]:
    if shutil.which('git') is None:
        raise RuntimeError('git is required to bootstrap fox-anki from the upstream repository.')

    result = subprocess.run(
        ['git', 'ls-remote', '--tags', '--refs', FOX_ANKI_REPO_URL],
        capture_output=True,
        text=True,
        check=True,
    )

    tags: list[tuple[str, str]] = []
    for line in result.stdout.splitlines():
        sha, ref = line.split('\t', 1)
        tag = ref.removeprefix('refs/tags/')
        if tag:
            tags.append((tag, sha.strip()))

    if not tags:
        raise RuntimeError(
            f'No git tags were found for {FOX_ANKI_REPO_URL}. Publish a tag before using remote bootstrap.'
        )

    latest_tag, latest_sha = max(tags, key=lambda item: parse_tag_sort_key(item[0]))
    return latest_tag, latest_sha



def resolve_source_spec() -> SourceSpec:
    local_repo = os.environ.get(FOX_ANKI_REPO_PATH_ENV)
    if local_repo:
        source_path = validate_source_path(Path(local_repo).expanduser().resolve())
        return SourceSpec(
            mode='local',
            repo=str(source_path),
            ref='working-tree',
            revision=git_head_revision(source_path),
            fingerprint=compute_source_fingerprint(source_path),
            source_path=source_path,
        )

    latest_tag, latest_sha = resolve_latest_remote_tag()
    return SourceSpec(
        mode='remote-tag',
        repo=FOX_ANKI_REPO_URL,
        ref=latest_tag,
        revision=latest_sha,
        fingerprint=None,
    )



def expected_bootstrap_state(source_spec: SourceSpec, bootstrap_python: Path) -> dict[str, object]:
    return {
        'bootstrap_python': str(bootstrap_python),
        'dependency_specs': DEPENDENCY_SPECS,
        'source_fingerprint': source_spec.fingerprint,
        'source_mode': source_spec.mode,
        'source_ref': source_spec.ref,
        'source_repo': source_spec.repo,
        'source_revision': source_spec.revision,
    }



def load_bootstrap_state() -> dict[str, object] | None:
    if not BOOTSTRAP_STATE.exists():
        return None
    return json.loads(BOOTSTRAP_STATE.read_text())



def write_bootstrap_state(state: dict[str, object]) -> None:
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    BOOTSTRAP_STATE.write_text(json.dumps(state, indent=2, sort_keys=True) + '\n')



def remove_existing_runtime_source() -> None:
    HIDDEN_RUNTIME.mkdir(parents=True, exist_ok=True)
    for child in HIDDEN_RUNTIME.iterdir():
        if child.name in PRESERVED_NAMES:
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()



def sync_tree_into_runtime(source_root: Path) -> None:
    remove_existing_runtime_source()

    def ignore(directory: str, names: list[str]) -> set[str]:
        directory_path = Path(directory)
        ignored: set[str] = set()
        for name in names:
            candidate = directory_path / name
            if should_ignore_path(candidate, source_root):
                ignored.add(name)
        return ignored

    for child in source_root.iterdir():
        if should_ignore_path(child, source_root):
            continue
        destination = HIDDEN_RUNTIME / child.name
        if child.is_dir():
            shutil.copytree(child, destination, dirs_exist_ok=True, ignore=ignore)
        else:
            shutil.copyfile(child, destination)



def sync_local_runtime(source_spec: SourceSpec) -> None:
    assert source_spec.source_path is not None
    sync_tree_into_runtime(source_spec.source_path)



def sync_remote_runtime(source_spec: SourceSpec) -> None:
    with tempfile.TemporaryDirectory(prefix='fox-anki-bootstrap-') as temp_dir:
        checkout_path = Path(temp_dir) / 'fox-anki'
        run([
            'git',
            'clone',
            '--depth',
            '1',
            '--branch',
            source_spec.ref,
            source_spec.repo,
            str(checkout_path),
        ])
        validate_source_path(checkout_path)
        sync_tree_into_runtime(checkout_path)



def sync_runtime_source(source_spec: SourceSpec) -> None:
    if source_spec.mode == 'local':
        sync_local_runtime(source_spec)
        return
    if source_spec.mode == 'remote-tag':
        sync_remote_runtime(source_spec)
        return
    raise RuntimeError(f'Unsupported fox-anki source mode: {source_spec.mode}')



def runtime_is_healthy() -> bool:
    return HIDDEN_RUNTIME.exists() and all((HIDDEN_RUNTIME / path).exists() for path in RUNTIME_REQUIRED_PATHS)



def venv_is_healthy() -> bool:
    return VENV_PYTHON.exists() and VENV_CLI.exists()



def cache_is_fresh(source_spec: SourceSpec, bootstrap_python: Path) -> bool:
    return (
        runtime_is_healthy()
        and venv_is_healthy()
        and load_bootstrap_state() == expected_bootstrap_state(source_spec, bootstrap_python)
    )



def ensure_venv(bootstrap_python: Path, state: dict[str, object]) -> None:
    previous_state = load_bootstrap_state() or {}
    should_recreate = previous_state.get('bootstrap_python') not in {None, str(bootstrap_python)}

    if should_recreate and VENV_ROOT.exists():
        shutil.rmtree(VENV_ROOT)

    if not venv_is_healthy():
        run([str(bootstrap_python), '-m', 'venv', str(VENV_ROOT)])

    run([str(VENV_PYTHON), '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel'])
    run([str(VENV_PYTHON), '-m', 'pip', 'install', *DEPENDENCY_SPECS])
    run([str(VENV_PYTHON), '-m', 'pip', 'install', '-e', str(HIDDEN_RUNTIME)])
    write_bootstrap_state(state)



def main() -> None:
    bootstrap_python = select_bootstrap_python()
    source_spec = resolve_source_spec()
    state = expected_bootstrap_state(source_spec, bootstrap_python)

    if cache_is_fresh(source_spec, bootstrap_python):
        print('bootstrap-cache-hit')
    else:
        sync_runtime_source(source_spec)
        ensure_venv(bootstrap_python, state)

    print('bootstrap-ready')
    print(f'source_mode={source_spec.mode}')
    print(f'source_repo={source_spec.repo}')
    print(f'source_ref={source_spec.ref}')
    print(f'source_revision={source_spec.revision}')
    print(f'runtime_root={RUNTIME_ROOT}')
    print(f'checkout={HIDDEN_RUNTIME}')
    print(f'bootstrap_python={bootstrap_python}')
    print(f'python={VENV_PYTHON}')
    print(f'cli={VENV_CLI}')


if __name__ == '__main__':
    main()
