#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_ROOT = Path.cwd() / 'output' / 'anki-leetcode'
WORKSPACE_ROOT = RUNTIME_ROOT / '.anki-leetcode'
CARDS_ROOT = WORKSPACE_ROOT / 'cards'
HIDDEN_RUNTIME = RUNTIME_ROOT / '.fox-anki'
VENV_PYTHON = HIDDEN_RUNTIME / '.venv' / 'bin' / 'python'
VENV_CLI = HIDDEN_RUNTIME / '.venv' / 'bin' / 'fox-anki'
BOOTSTRAP_SCRIPT = SKILL_ROOT / 'scripts' / 'bootstrap_fox_anki.py'
BUILD_SCRIPT = SKILL_ROOT / 'scripts' / 'build_leetcode_apkg.py'
MERGE_SCRIPT = SKILL_ROOT / 'scripts' / 'merge_leetcode_deck.py'
NORMALIZE_NOTE_TYPE_SCRIPT = SKILL_ROOT / 'scripts' / 'normalize_leetcode_notetype.py'
MAIN_COLLECTION = Path('~/Library/Application Support/Anki2/User 1/collection.anki2').expanduser()
RUNTIME_SENTINEL_ENV = 'ANKI_LEETCODE_RUNTIME'
DECK_NAME = 'LeetCode'
NOTE_TYPE = 'LeetCode Basic'
QUESTION_QUERY = (
    'query questionData($titleSlug: String!) {'
    ' question(titleSlug: $titleSlug) {'
    ' questionFrontendId title titleSlug content translatedTitle translatedContent'
    ' exampleTestcases topicTags { name slug translatedName } hints difficulty'
    ' }'
    '}'
)
URL_PATTERN = re.compile(r'^https?://leetcode\.(?P<host>cn|com)/problems/(?P<slug>[^/]+)/?(?:description/?)?$', re.IGNORECASE)
CARD_LANGUAGE_TOKENS = {
    'zh': 'zh-CN',
    'zh-cn': 'zh-CN',
    'cn': 'zh-CN',
    'chinese': 'zh-CN',
    '中文': 'zh-CN',
    '简体中文': 'zh-CN',
    'en': 'en',
    'english': 'en',
}
CODE_LANGUAGE_LABELS = {
    'python': 'Python 3',
    'java': 'Java',
    'cpp': 'C++',
    'javascript': 'JavaScript',
    'typescript': 'TypeScript',
    'go': 'Go',
}


CODE_LANGUAGE_ALIASES = {
    'python3': 'python',
    'py3': 'python',
    'c++': 'cpp',
    'cplusplus': 'cpp',
    'js': 'javascript',
    'ts': 'typescript',
    'golang': 'go',
}

yaml = None


@dataclass(slots=True)
class InvocationOptions:
    urls: list[str]
    card_language: str | None
    code_language: str
    refresh: bool
    rebuild: bool
    import_anyway: bool
    skip_import: bool
    close_anki_if_running: bool
    collection_path: Path
    deck_name: str
    json_output: bool
    dry_run: bool


@dataclass(slots=True)
class ProblemCard:
    url: str
    slug: str
    frontend_id: str
    yaml_path: Path
    changed: bool


@dataclass(slots=True)
class RunStatus:
    yaml_paths: list[Path]
    reused_yaml_paths: list[Path]
    rebuilt: bool
    imported: bool
    anki_closed_reopened: bool
    skipped_reason: str | None
    dry_run: bool
    planned_actions: list[str]


class SkillError(RuntimeError):
    pass


class ClaudeGenerationError(SkillError):
    pass


class LeetCodeFetchError(SkillError):
    pass


class LiteralDumper:  # placeholder; initialized after runtime re-exec
    pass


class _LiteralSafeDumper:  # placeholder; initialized after runtime re-exec
    pass



def ensure_runtime_and_reexec() -> None:
    if VENV_PYTHON.exists() and Path(sys.prefix).resolve() == HIDDEN_RUNTIME.joinpath('.venv').resolve():
        return

    if not VENV_PYTHON.exists():
        subprocess.run([sys.executable, str(BOOTSTRAP_SCRIPT)], check=True)

    env = os.environ.copy()
    env[RUNTIME_SENTINEL_ENV] = '1'
    os.execve(str(VENV_PYTHON), [str(VENV_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]], env)



def init_runtime_dependencies() -> None:
    global yaml, LiteralDumper, _LiteralSafeDumper

    import yaml as yaml_module

    yaml = yaml_module

    class _LiteralSafeDumperImpl(yaml.SafeDumper):
        pass

    def _represent_str(dumper: yaml.SafeDumper, data: str):
        style = '|' if '\n' in data else None
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style=style)

    _LiteralSafeDumperImpl.add_representer(str, _represent_str)
    _LiteralSafeDumper = _LiteralSafeDumperImpl
    LiteralDumper = _LiteralSafeDumperImpl



def normalize_code_language(raw: str | None) -> str:
    if raw is None:
        return 'python'
    normalized = raw.strip().lower()
    return CODE_LANGUAGE_ALIASES.get(normalized, normalized)



def parse_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Generate or reuse LeetCode Anki card YAMLs, rebuild leetcode.apkg, and optionally import it.',
    )
    parser.add_argument('items', nargs='+', help='One or more LeetCode problem URLs followed by optional card language and code language.')
    parser.add_argument('--refresh', action='store_true', help='Regenerate requested problem YAMLs even if they already exist.')
    parser.add_argument('--rebuild', action='store_true', help='Force an APKG rebuild even when all YAMLs are reused.')
    parser.add_argument('--import-anyway', action='store_true', help='Force the macOS import flow even when all YAMLs are reused.')
    parser.add_argument('--skip-import', action='store_true', help='Skip importing into an Anki collection after rebuilding.')
    parser.add_argument('--close-anki-if-running', action='store_true', help='Allow the script to close and reopen Anki during import.')
    parser.add_argument('--collection', default=str(MAIN_COLLECTION), help='Target Anki collection path for import. Defaults to the main macOS collection.')
    parser.add_argument('--deck', default=DECK_NAME, help='Deck name to export/import. Defaults to LeetCode.')
    parser.add_argument('--json', action='store_true', help='Emit machine-readable JSON status output.')
    parser.add_argument('--dry-run', action='store_true', help='Preview reuse, rebuild, and import decisions without writing YAML, rebuilding, or importing.')
    return parser.parse_args()



def normalize_invocation(args: argparse.Namespace) -> InvocationOptions:
    urls: list[str] = []
    trailing: list[str] = []
    for item in args.items:
        if URL_PATTERN.fullmatch(item.strip()):
            urls.append(item.strip())
        else:
            trailing.append(item.strip())

    if not urls:
        raise SkillError('At least one valid LeetCode problem URL is required.')

    if len(trailing) > 2:
        raise SkillError('Arguments must follow: <urls...> [card language] [code language].')

    card_language: str | None = None
    code_language_raw: str | None = None

    if len(trailing) == 1:
        token = trailing[0].lower()
        if token in CARD_LANGUAGE_TOKENS:
            card_language = CARD_LANGUAGE_TOKENS[token]
        else:
            code_language_raw = trailing[0]
    elif len(trailing) == 2:
        token = trailing[0].lower()
        if token not in CARD_LANGUAGE_TOKENS:
            raise SkillError('When two trailing arguments are provided, the first must be a card language override.')
        card_language = CARD_LANGUAGE_TOKENS[token]
        code_language_raw = trailing[1]

    code_language = normalize_code_language(code_language_raw)

    return InvocationOptions(
        urls=urls,
        card_language=card_language,
        code_language=code_language,
        refresh=args.refresh,
        rebuild=args.rebuild,
        import_anyway=args.import_anyway,
        skip_import=args.skip_import,
        close_anki_if_running=args.close_anki_if_running,
        collection_path=Path(args.collection).expanduser().resolve(),
        deck_name=args.deck,
        json_output=args.json,
        dry_run=args.dry_run,
    )



def fetch_graphql_question(slug: str, host: str) -> dict[str, Any]:
    endpoint = f'https://leetcode.{host}/graphql'
    referer = (
        f'https://leetcode.{host}/problems/{slug}/description/'
        if host == 'cn'
        else f'https://leetcode.{host}/problems/{slug}/'
    )
    payload = json.dumps({'query': QUESTION_QUERY, 'variables': {'titleSlug': slug}}).encode('utf-8')
    request = urllib.request.Request(
        endpoint,
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0',
            'Referer': referer,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode('utf-8')
    except urllib.error.HTTPError as exc:
        raise LeetCodeFetchError(f'Failed to fetch LeetCode GraphQL for {slug} from {host}: HTTP {exc.code}') from exc
    except urllib.error.URLError as exc:
        raise LeetCodeFetchError(f'Failed to fetch LeetCode GraphQL for {slug} from {host}: {exc.reason}') from exc

    payload_obj = json.loads(raw)
    question = payload_obj.get('data', {}).get('question')
    if not question:
        raise LeetCodeFetchError(f'No question data returned for slug: {slug}')
    return question



def fetch_problem_bundle(url: str, card_language: str | None) -> dict[str, Any]:
    match = URL_PATTERN.fullmatch(url)
    if match is None:
        raise SkillError(f'Invalid LeetCode problem URL: {url}')

    slug = match.group('slug').lower()
    host = match.group('host').lower()
    primary_host = host
    hosts_to_fetch = {primary_host}
    if card_language == 'zh-CN':
        hosts_to_fetch.add('cn')
    if card_language == 'en':
        hosts_to_fetch.add('com')

    fetched: dict[str, dict[str, Any]] = {}
    for candidate_host in hosts_to_fetch:
        try:
            fetched[candidate_host] = fetch_graphql_question(slug, candidate_host)
        except LeetCodeFetchError:
            if candidate_host == primary_host:
                raise

    primary = fetched[primary_host]
    frontend_id = str(primary['questionFrontendId'])
    topic_tags = primary.get('topicTags') or []

    english_source = fetched.get('com') or primary
    chinese_source = fetched.get('cn') or primary

    english_title = english_source.get('title') or primary.get('title')
    english_content = english_source.get('content') or primary.get('content')
    chinese_title = chinese_source.get('translatedTitle') or chinese_source.get('title')
    chinese_content = chinese_source.get('translatedContent') or chinese_source.get('content')

    return {
        'url': url,
        'slug': slug,
        'host': host,
        'frontend_id': frontend_id,
        'difficulty': primary.get('difficulty') or '',
        'topic_tags': topic_tags,
        'hints': primary.get('hints') or [],
        'english_title': english_title,
        'english_content': english_content,
        'chinese_title': chinese_title,
        'chinese_content': chinese_content,
    }



def translate_problem_content(title: str, content_html: str, target_language: str) -> tuple[str, str]:
    prompt = (
        'Translate the following LeetCode title and HTML content for an Anki card. '
        'Preserve the HTML structure and semantic meaning. Do not add or remove sections. '
        f'Target language: {target_language}.\n\n'
        f'Title: {title}\n\n'
        f'HTML content:\n{content_html}'
    )
    schema = {
        'type': 'object',
        'properties': {
            'title': {'type': 'string'},
            'content_html': {'type': 'string'},
        },
        'required': ['title', 'content_html'],
        'additionalProperties': False,
    }
    result = call_claude_structured(prompt, schema)
    return result['title'].strip(), result['content_html'].strip()



def select_card_content(problem: dict[str, Any], card_language: str | None) -> tuple[str, str, str]:
    default_language = 'zh-CN' if problem['host'] == 'cn' else 'en'
    final_language = card_language or default_language

    if final_language == 'zh-CN':
        title = problem.get('chinese_title')
        content_html = problem.get('chinese_content')
        if not title or not content_html:
            english_title = problem.get('english_title') or ''
            english_content = problem.get('english_content') or ''
            title, content_html = translate_problem_content(english_title, english_content, 'Simplified Chinese')
        return final_language, title, content_html

    title = problem.get('english_title')
    content_html = problem.get('english_content')
    if not title or not content_html:
        chinese_title = problem.get('chinese_title') or ''
        chinese_content = problem.get('chinese_content') or ''
        title, content_html = translate_problem_content(chinese_title, chinese_content, 'English')
    return final_language, title, content_html



def call_claude_structured(prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
    if shutil.which('claude') is None:
        raise ClaudeGenerationError('Claude CLI is required to generate card explanations and solutions.')

    command = [
        'claude',
        '-p',
        prompt,
        '--bare',
        '--tools',
        '',
        '--output-format',
        'json',
        '--json-schema',
        json.dumps(schema, ensure_ascii=False, separators=(',', ':')),
        '--effort',
        'medium',
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise ClaudeGenerationError(result.stderr.strip() or result.stdout.strip() or 'Claude CLI generation failed.')

    payload = json.loads(result.stdout)
    structured_output = payload.get('structured_output')
    if not isinstance(structured_output, dict):
        raise ClaudeGenerationError('Claude CLI did not return structured output.')
    return structured_output



def generate_solution_bundle(problem: dict[str, Any], card_language: str, code_language: str, title: str, content_html: str) -> dict[str, Any]:
    code_label = CODE_LANGUAGE_LABELS.get(code_language, code_language)
    prose_language = 'Simplified Chinese' if card_language == 'zh-CN' else 'English'
    topic_slugs = [tag['slug'] for tag in problem['topic_tags'] if tag.get('slug')]
    prompt = (
        'You are generating structured study-card content for a LeetCode problem. '
        'Return only the requested JSON fields.\n\n'
        f'Use {prose_language} for all prose fields.\n'
        f'Generate a complete accepted solution in {code_label}.\n'
        'Use 2 to 4 concise approach bullets.\n'
        'Return time_complexity and space_complexity as Big-O formulas only, such as O(n^2) or O(1).\n'
        'Return algorithm_tags as 2 to 4 lowercase English slugs such as array or two-pointers.\n'
        'Do not include markdown fences in solution_code.\n\n'
        f'Problem title: {title}\n'
        f'Difficulty: {problem.get("difficulty", "")}\n'
        f'Topic tags: {", ".join(topic_slugs)}\n'
        f'Hints: {json.dumps(problem.get("hints", []), ensure_ascii=False)}\n\n'
        f'Problem HTML:\n{content_html}'
    )
    schema = {
        'type': 'object',
        'properties': {
            'approach_bullets': {
                'type': 'array',
                'items': {'type': 'string'},
                'minItems': 2,
                'maxItems': 4,
            },
            'time_complexity': {'type': 'string'},
            'space_complexity': {'type': 'string'},
            'solution_code': {'type': 'string'},
            'algorithm_tags': {
                'type': 'array',
                'items': {'type': 'string'},
                'minItems': 2,
                'maxItems': 4,
            },
        },
        'required': ['approach_bullets', 'time_complexity', 'space_complexity', 'solution_code', 'algorithm_tags'],
        'additionalProperties': False,
    }
    return call_claude_structured(prompt, schema)



def derive_yaml_path(frontend_id: str, slug: str) -> Path:
    normalized_slug = slug.lower().replace('-', '_')
    return CARDS_ROOT / f'leetcode_{frontend_id}_{normalized_slug}.yaml'



def compose_front_html(title: str, url: str, content_html: str) -> str:
    return (
        '<div style="text-align: left;">\n'
        f'<strong><a href="{html.escape(url, quote=True)}">{html.escape(title)}</a></strong><br><br>\n'
        f'{content_html.strip()}\n'
        '</div>\n'
    )



def compose_back_html(card_language: str, code_language: str, solution_bundle: dict[str, Any]) -> str:
    code_label = CODE_LANGUAGE_LABELS.get(code_language, code_language)
    bullets = ''.join(f'  <li>{html.escape(item)}</li>\n' for item in solution_bundle['approach_bullets'])
    escaped_code = html.escape(solution_bundle['solution_code'])

    if card_language == 'zh-CN':
        return (
            '<div style="text-align: left;">\n'
            '<strong>思路</strong>\n'
            '<ul>\n'
            f'{bullets}'
            '</ul>\n'
            '<strong>复杂度</strong>\n'
            '<ul>\n'
            f'  <li>时间复杂度：{html.escape(solution_bundle["time_complexity"])}</li>\n'
            f'  <li>额外空间复杂度：{html.escape(solution_bundle["space_complexity"])}</li>\n'
            '</ul>\n'
            f'<strong>题解（{html.escape(code_label)}）</strong>\n'
            f'<pre><code>{escaped_code}</code></pre>\n'
            '</div>\n'
        )

    return (
        '<div style="text-align: left;">\n'
        '<strong>Approach</strong>\n'
        '<ul>\n'
        f'{bullets}'
        '</ul>\n'
        '<strong>Complexity</strong>\n'
        '<ul>\n'
        f'  <li>Time complexity: {html.escape(solution_bundle["time_complexity"])}</li>\n'
        f'  <li>Extra space complexity: {html.escape(solution_bundle["space_complexity"])}</li>\n'
        '</ul>\n'
        f'<strong>Solution ({html.escape(code_label)})</strong>\n'
        f'<pre><code>{escaped_code}</code></pre>\n'
        '</div>\n'
    )



def write_yaml_entries(path: Path, entries: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as handle:
        yaml.dump(entries, handle, Dumper=LiteralDumper, allow_unicode=True, sort_keys=False, width=100000)



def load_yaml_entries(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding='utf-8') as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, list) or not data:
        raise SkillError(f'Expected a non-empty YAML list in {path}')
    return data



def create_card_entry(problem: dict[str, Any], final_language: str, title: str, content_html: str, code_language: str) -> dict[str, Any]:
    solution_bundle = generate_solution_bundle(problem, final_language, code_language, title, content_html)
    algorithm_tags: list[str] = []
    for tag in solution_bundle['algorithm_tags']:
        slug = tag.strip().lower()
        if slug and slug not in algorithm_tags:
            algorithm_tags.append(slug)
    if len(algorithm_tags) < 2:
        for topic in problem['topic_tags']:
            slug = topic.get('slug', '').strip().lower()
            if slug and slug not in algorithm_tags:
                algorithm_tags.append(slug)
            if len(algorithm_tags) >= 2:
                break
    algorithm_tags = algorithm_tags[:4]

    return {
        'type': NOTE_TYPE,
        'code_language': code_language,
        'tags': ['leetcode', f'leetcode-{problem["frontend_id"]}', *algorithm_tags],
        'fields': {
            'Front': compose_front_html(title, problem['url'], content_html),
            'Back': compose_back_html(final_language, code_language, solution_bundle),
        },
    }



def index_existing_yaml_by_slug() -> dict[str, Path]:
    indexed: dict[str, Path] = {}
    for path in sorted(CARDS_ROOT.glob('leetcode_*.yaml')):
        match = re.fullmatch(r'leetcode_\d+_(.+)\.yaml', path.name)
        if match is None:
            continue
        indexed.setdefault(match.group(1), path)
    return indexed



def build_problem_cards(options: InvocationOptions) -> tuple[list[ProblemCard], bool]:
    problem_cards: list[ProblemCard] = []
    any_changed = False
    existing_yaml_by_slug = index_existing_yaml_by_slug() if not options.refresh else {}

    for url in options.urls:
        match = URL_PATTERN.fullmatch(url)
        assert match is not None
        url_slug = match.group('slug').lower().replace('-', '_')

        existing_yaml = existing_yaml_by_slug.get(url_slug)
        if existing_yaml is not None:
            problem_cards.append(
                ProblemCard(
                    url=url,
                    slug=url_slug,
                    frontend_id=existing_yaml.stem.split('_', 2)[1],
                    yaml_path=existing_yaml,
                    changed=False,
                )
            )
            continue

        problem = fetch_problem_bundle(url, options.card_language)
        final_language, title, content_html = select_card_content(problem, options.card_language)
        yaml_path = derive_yaml_path(problem['frontend_id'], problem['slug'])

        if yaml_path.exists() and not options.refresh:
            problem_cards.append(
                ProblemCard(
                    url=url,
                    slug=problem['slug'],
                    frontend_id=problem['frontend_id'],
                    yaml_path=yaml_path,
                    changed=False,
                )
            )
            continue

        entry = create_card_entry(problem, final_language, title, content_html, options.code_language)
        write_yaml_entries(yaml_path, [entry])
        problem_cards.append(
            ProblemCard(
                url=url,
                slug=problem['slug'],
                frontend_id=problem['frontend_id'],
                yaml_path=yaml_path,
                changed=True,
            )
        )
        any_changed = True

    return problem_cards, any_changed



def build_batch_yaml(problem_cards: list[ProblemCard]) -> Path:
    batch_entries: list[dict[str, Any]] = []
    for problem_card in problem_cards:
        batch_entries.extend(load_yaml_entries(problem_card.yaml_path))
    batch_path = WORKSPACE_ROOT / 'batch_current.yaml'
    write_yaml_entries(batch_path, batch_entries)
    return batch_path



def rebuild_apkg(batch_path: Path, deck_name: str) -> None:
    subprocess.run(
        [
            str(VENV_PYTHON),
            str(BUILD_SCRIPT),
            str(batch_path),
            str(RUNTIME_ROOT / 'leetcode.apkg'),
            '--deck',
            deck_name,
        ],
        check=True,
    )



def is_macos() -> bool:
    return sys.platform == 'darwin'



def _run_osascript(*lines: str) -> subprocess.CompletedProcess[str]:
    command = ['osascript']
    for line in lines:
        command.extend(['-e', line])
    return subprocess.run(command, capture_output=True, text=True)



def is_anki_running() -> bool:
    if not is_macos():
        return False
    result = _run_osascript('application "Anki" is running')
    if result.returncode != 0:
        return False
    return result.stdout.strip().lower() == 'true'



def confirm_close_anki_if_needed(allow_close: bool) -> bool:
    if not is_anki_running():
        return False

    if allow_close:
        return True

    if sys.stdin.isatty() and sys.stdout.isatty():
        answer = input('Anki is running. Close it, import, and reopen it? [y/N] ').strip().lower()
        return answer in {'y', 'yes'}

    raise SkillError('Anki is running. Re-run with --close-anki-if-running after confirmation.')



def close_anki() -> None:
    _run_osascript('tell application "Anki" to quit')
    for _ in range(40):
        if not is_anki_running():
            return
        time.sleep(0.25)
    raise SkillError('Anki is still running after the quit request.')



def reopen_anki() -> None:
    subprocess.run(['open', '-a', 'Anki'], check=True)



def collection_has_merge_candidates(collection_path: Path) -> bool:
    from anki.collection import Collection

    col = Collection(str(collection_path))
    try:
        deck_names = [deck.name for deck in col.decks.all_names_and_ids()]
    finally:
        col.close()

    return any(name.startswith(f'{DECK_NAME}::') for name in deck_names)



def merge_decks_if_needed(collection_path: Path) -> None:
    if not collection_has_merge_candidates(collection_path):
        return
    subprocess.run([str(VENV_PYTHON), str(MERGE_SCRIPT), '--collection', str(collection_path)], check=True)



def import_apkg(collection_path: Path) -> None:
    subprocess.run(
        [
            str(VENV_CLI),
            'import',
            'apkg',
            str(RUNTIME_ROOT / 'leetcode.apkg'),
            '--merge-notetypes',
            '--update-notes',
            'always',
            '--update-notetypes',
            'always',
            '--collection',
            str(collection_path),
        ],
        check=True,
    )



def normalize_leetcode_notetypes(collection_path: Path) -> None:
    subprocess.run(
        [
            str(VENV_PYTHON),
            str(NORMALIZE_NOTE_TYPE_SCRIPT),
            '--collection',
            str(collection_path),
        ],
        check=True,
    )



def run_import_flow(options: InvocationOptions) -> tuple[bool, bool]:
    if options.skip_import or not is_macos():
        return False, False

    if not options.collection_path.exists():
        raise SkillError(f'Collection not found: {options.collection_path}')

    closed_and_reopened = False
    should_close = confirm_close_anki_if_needed(options.close_anki_if_running)
    if should_close:
        close_anki()
        closed_and_reopened = True

    merge_decks_if_needed(options.collection_path)
    import_apkg(options.collection_path)
    normalize_leetcode_notetypes(options.collection_path)

    if closed_and_reopened:
        reopen_anki()

    return True, closed_and_reopened



def format_status(status: RunStatus, as_json: bool) -> str:
    payload = {
        'yaml_paths': [str(path) for path in status.yaml_paths],
        'reused_yaml_paths': [str(path) for path in status.reused_yaml_paths],
        'rebuilt': status.rebuilt,
        'imported': status.imported,
        'anki_closed_reopened': status.anki_closed_reopened,
        'skipped_reason': status.skipped_reason,
        'dry_run': status.dry_run,
        'planned_actions': status.planned_actions,
    }
    if as_json:
        return json.dumps(payload, ensure_ascii=False, indent=2)

    lines: list[str] = []
    if status.dry_run:
        lines.append('dry run planned actions:')
        lines.extend(f'- {action}' for action in status.planned_actions)
        if status.yaml_paths:
            lines.append('would generate or update YAML paths:')
            lines.extend(f'- {path}' for path in status.yaml_paths)
        if status.reused_yaml_paths:
            lines.append('would reuse YAML paths:')
            lines.extend(f'- {path}' for path in status.reused_yaml_paths)
        return '\n'.join(lines)

    if status.skipped_reason:
        lines.append(status.skipped_reason)
        if status.reused_yaml_paths:
            lines.append('reused YAML paths:')
            lines.extend(f'- {path}' for path in status.reused_yaml_paths)
        return '\n'.join(lines)

    lines.append('generated or updated YAML paths:')
    lines.extend(f'- {path}' for path in status.yaml_paths)
    lines.append('leetcode.apkg updated: yes' if status.rebuilt else 'leetcode.apkg updated: no')
    lines.append(f'main collection imported: {"yes" if status.imported else "no"}')
    lines.append(f'Anki closed and reopened: {"yes" if status.anki_closed_reopened else "no"}')
    return '\n'.join(lines)



def run(options: InvocationOptions) -> RunStatus:
    CARDS_ROOT.mkdir(parents=True, exist_ok=True)

    problem_cards, any_changed = build_problem_cards(options)
    changed_paths = [card.yaml_path for card in problem_cards if card.changed]
    reused_paths = [card.yaml_path for card in problem_cards if not card.changed]

    force_rebuild = options.rebuild or options.import_anyway
    if not any_changed and not force_rebuild:
        planned_actions = ['reuse existing YAML files', 'skip rebuild', 'skip import']
        return RunStatus(
            yaml_paths=[],
            reused_yaml_paths=reused_paths,
            rebuilt=False,
            imported=False,
            anki_closed_reopened=False,
            skipped_reason='Existing YAML files were reused and no rebuild/import was needed.',
            dry_run=options.dry_run,
            planned_actions=planned_actions,
        )

    planned_yaml_paths = changed_paths if changed_paths else [card.yaml_path for card in problem_cards]
    planned_actions = ['rebuild leetcode.apkg']
    if is_macos() and not options.skip_import:
        if is_anki_running():
            planned_actions.append('close Anki before import')
            planned_actions.append('reopen Anki after import')
        planned_actions.append(f'import package into {options.collection_path}')
        planned_actions.append(f'normalize LeetCode Basic variants in {options.collection_path}')

    if options.dry_run:
        return RunStatus(
            yaml_paths=planned_yaml_paths,
            reused_yaml_paths=reused_paths,
            rebuilt=False,
            imported=False,
            anki_closed_reopened=False,
            skipped_reason=None,
            dry_run=True,
            planned_actions=planned_actions,
        )

    batch_path = build_batch_yaml(problem_cards)
    rebuild_apkg(batch_path, options.deck_name)
    imported, closed_and_reopened = run_import_flow(options)

    return RunStatus(
        yaml_paths=planned_yaml_paths,
        reused_yaml_paths=reused_paths,
        rebuilt=True,
        imported=imported,
        anki_closed_reopened=closed_and_reopened,
        skipped_reason=None,
        dry_run=False,
        planned_actions=planned_actions,
    )



def main() -> int:
    try:
        ensure_runtime_and_reexec()
        init_runtime_dependencies()
        args = parse_cli_args()
        options = normalize_invocation(args)
        status = run(options)
        print(format_status(status, options.json_output))
        return 0
    except SkillError as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as exc:
        print(f'error: command failed with exit code {exc.returncode}', file=sys.stderr)
        return exc.returncode or 1


if __name__ == '__main__':
    raise SystemExit(main())
