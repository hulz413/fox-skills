#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import yaml
from anki.collection import Collection
from anki.models import NotetypeDict
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer, TextLexer, get_lexer_by_name

CODE_BLOCK_PATTERN = re.compile(
    r'<pre(?:\s[^>]*)?><code(?:\s[^>]*)?>(.*?)</code></pre>',
    re.IGNORECASE | re.DOTALL,
)
LEETCODE_TAG_PATTERN = re.compile(r'leetcode-\d+')
STOCK_NOTE_TYPE = 'Basic'
TARGET_NOTE_TYPE = 'LeetCode Basic'
EXPECTED_FIELD_NAMES = ('Front', 'Back')
EXPECTED_TEMPLATE_NAMES = ('Card 1',)
EXPECTED_BASIC_STOCK_KIND = 1
RUNTIME_ROOT = Path.cwd() / 'output' / 'anki-leetcode'
HIDDEN_RUNTIME = RUNTIME_ROOT / '.fox-anki'
VENV_CLI = HIDDEN_RUNTIME / '.venv' / 'bin' / 'fox-anki'
BUILD_ROOT = HIDDEN_RUNTIME / 'build-current'
BUILD_COLLECTION = BUILD_ROOT / 'collection.anki2'



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Build leetcode.apkg from a batch YAML file using a fresh fox-anki-backed collection.',
    )
    parser.add_argument('input_file', help='Batch YAML file containing one or more cards.')
    parser.add_argument('output_file', help='Output APKG path.')
    parser.add_argument('--deck', default='LeetCode', help='Deck name to export.')
    return parser.parse_args()



def get_code_lexer(code_language: str | None):
    normalized = (code_language or 'python').strip().lower()
    aliases = {
        'python3': 'python',
        'py3': 'python',
        'c++': 'cpp',
        'cplusplus': 'cpp',
        'js': 'javascript',
        'ts': 'typescript',
        'golang': 'go',
    }
    normalized = aliases.get(normalized, normalized)

    try:
        return get_lexer_by_name(normalized, stripall=False)
    except Exception:
        if normalized == 'python':
            return PythonLexer(stripall=False)
        return TextLexer(stripall=False)



def normalize_code_language(code_language: str | None) -> str:
    lexer = get_code_lexer(code_language)
    aliases = {
        'python3': 'python',
        'py3': 'python',
        'c++': 'cpp',
        'cplusplus': 'cpp',
        'js': 'javascript',
        'ts': 'typescript',
        'golang': 'go',
    }
    requested = (code_language or 'python').strip().lower()
    normalized = aliases.get(requested, requested)
    if normalized:
        return normalized
    return getattr(lexer, 'name', 'text').lower()



def highlight_code_blocks(content: Any, code_language: str = 'python') -> Any:
    if not isinstance(content, str):
        return content

    formatter = HtmlFormatter(noclasses=True, nowrap=True, nobackground=True)
    lexer = get_code_lexer(code_language)

    def replace(match: re.Match[str]) -> str:
        raw_code = match.group(1)
        if '<span ' in raw_code:
            return match.group(0)

        highlighted_code = highlight(html.unescape(raw_code), lexer, formatter).rstrip()
        return (
            '<pre style="text-align: left; background: #f6f8fa; color: #24292f; '
            'padding: 12px 14px; border-radius: 8px; overflow-x: auto; white-space: pre; '
            "font-size: 13px; line-height: 1.5; font-family: Menlo, Monaco, Consolas, 'Courier New', monospace;\"><code>"
            f'{highlighted_code}'
            '</code></pre>'
        )

    return CODE_BLOCK_PATTERN.sub(replace, content)



def parse_cards(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding='utf-8') as file:
        cards = yaml.safe_load(file)

    if not isinstance(cards, list) or not cards:
        raise RuntimeError('Batch YAML must contain a non-empty list of cards.')

    parsed_cards: list[dict[str, Any]] = []
    for card in cards:
        if not isinstance(card, dict):
            raise RuntimeError('Each card entry must be a mapping.')

        note_type = card.get('type')
        if note_type != TARGET_NOTE_TYPE:
            raise RuntimeError(f"anki-leetcode only supports type: {TARGET_NOTE_TYPE}")

        fields = card.get('fields')
        if not isinstance(fields, dict):
            raise RuntimeError("Attribute 'fields' is required in card definition")

        field_names = tuple(fields.keys())
        missing_fields = [field_name for field_name in EXPECTED_FIELD_NAMES if field_name not in fields]
        extra_fields = [field_name for field_name in fields if field_name not in EXPECTED_FIELD_NAMES]
        if missing_fields or extra_fields or field_names != EXPECTED_FIELD_NAMES:
            raise RuntimeError(
                'anki-leetcode cards must define exactly these fields in order: '
                + ', '.join(EXPECTED_FIELD_NAMES)
            )

        tags = card.get('tags', [])
        if tags is None:
            tags = []
        if not isinstance(tags, list):
            raise RuntimeError("Attribute 'tags' must be a list when provided")

        leetcode_card_tags = leetcode_tags({'tags': tags})
        if len(leetcode_card_tags) != 1:
            raise RuntimeError('Each anki-leetcode card must include exactly one leetcode-<id> tag.')

        code_language = normalize_code_language(card.get('code_language'))
        rendered_fields = {
            field_name: highlight_code_blocks(field_value, code_language)
            for field_name, field_value in fields.items()
        }

        parsed_cards.append(
            {
                'type': note_type,
                'code_language': code_language,
                'tags': [tag for tag in tags if isinstance(tag, str)],
                'fields': rendered_fields,
                'leetcode_tag': leetcode_card_tags[0],
            }
        )

    return parsed_cards



def ensure_build_root() -> None:
    BUILD_ROOT.mkdir(parents=True, exist_ok=True)



def ensure_deck(col: Collection, deck_name: str) -> int:
    deck_id = col.decks.id_for_name(deck_name)
    if deck_id is not None:
        return int(deck_id)
    result = col.decks.add_normal_deck_with_name(deck_name)
    return int(result.id)



def leetcode_tags(entry: dict[str, Any]) -> list[str]:
    return sorted(tag for tag in entry.get('tags', []) if isinstance(tag, str) and LEETCODE_TAG_PATTERN.fullmatch(tag))



def stable_guid(entry: dict[str, Any]) -> str:
    digest_source = entry['leetcode_tag']
    return hashlib.sha1(digest_source.encode('utf-8')).hexdigest()[:10]



def require_stock_basic_model(col: Collection) -> dict[str, Any]:
    model = col.models.by_name(STOCK_NOTE_TYPE)
    if model is None:
        raise RuntimeError(f'Model not found: {STOCK_NOTE_TYPE}')

    field_names = tuple(field['name'] for field in model['flds'])
    template_names = tuple(template['name'] for template in model['tmpls'])
    stock_kind = model.get('originalStockKind')

    if field_names != EXPECTED_FIELD_NAMES or template_names != EXPECTED_TEMPLATE_NAMES or stock_kind != EXPECTED_BASIC_STOCK_KIND:
        raise RuntimeError(
            'The fresh build collection does not contain the stock Basic note type '
            '(expected Front/Back, Card 1, originalStockKind=1).'
        )

    return model



def ensure_target_model(col: Collection) -> dict[str, Any]:
    stock_model = require_stock_basic_model(col)
    target_model = col.models.by_name(TARGET_NOTE_TYPE)
    if target_model is not None:
        field_names = tuple(field['name'] for field in target_model['flds'])
        template_names = tuple(template['name'] for template in target_model['tmpls'])
        stock_kind = target_model.get('originalStockKind')
        if field_names != EXPECTED_FIELD_NAMES or template_names != EXPECTED_TEMPLATE_NAMES or stock_kind != EXPECTED_BASIC_STOCK_KIND:
            raise RuntimeError(
                'Existing LeetCode Basic note type does not match the expected Basic-compatible schema.'
            )
        return target_model

    cloned_model = col.models.copy(stock_model, add=False)
    cloned_model['name'] = TARGET_NOTE_TYPE
    col.models.add(cloned_model)
    target_model = col.models.by_name(TARGET_NOTE_TYPE)
    if target_model is None:
        raise RuntimeError(f'Failed to create note type: {TARGET_NOTE_TYPE}')
    return target_model



def add_or_update_cards(cards: list[dict[str, Any]], deck_name: str) -> None:
    ensure_build_root()
    col = Collection(str(BUILD_COLLECTION))
    try:
        deck_id = ensure_deck(col, deck_name)
        target_model = ensure_target_model(col)

        existing_note_ids = {
            entry['leetcode_tag']: [int(note_id) for note_id in col.find_notes(f'tag:{entry["leetcode_tag"]}')]
            for entry in cards
        }

        for entry in cards:
            note_ids = existing_note_ids[entry['leetcode_tag']]
            if note_ids:
                note = col.get_note(note_ids[0])
                if note.mid != target_model['id']:
                    raise RuntimeError(
                        f"Existing note for {entry['leetcode_tag']} does not use the expected note type: {TARGET_NOTE_TYPE}"
                    )
            else:
                note = col.new_note(target_model)

            for field_name in EXPECTED_FIELD_NAMES:
                field_value = entry['fields'][field_name]
                if field_name not in note:
                    raise RuntimeError(f'Unknown field for {TARGET_NOTE_TYPE}: {field_name}')
                note[field_name] = field_value

            if note.fields_check() != 0:
                raise RuntimeError(f'Note fields failed validation for model: {TARGET_NOTE_TYPE}')

            note.guid = stable_guid(entry)

            tags = entry.get('tags', [])
            if tags:
                note.set_tags_from_str(' '.join(tags))

            if note_ids:
                col.update_note(note)
            else:
                col.add_note(note, deck_id)
    finally:
        col.close()



def export_apkg(output_file: Path, deck_name: str) -> None:
    if not VENV_CLI.exists():
        raise RuntimeError(f'fox-anki CLI not found: {VENV_CLI}')

    output_file.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            str(VENV_CLI),
            'export',
            'apkg',
            str(output_file),
            '--deck',
            deck_name,
            '--force',
            '--collection',
            str(BUILD_COLLECTION),
        ],
        check=True,
    )



def main() -> None:
    args = parse_args()
    input_file = Path(args.input_file).expanduser().resolve()
    output_file = Path(args.output_file).expanduser().resolve()

    if not input_file.exists():
        raise RuntimeError(f'Input file does not exist: {input_file}')

    cards = parse_cards(input_file)
    add_or_update_cards(cards, args.deck)
    export_apkg(output_file, args.deck)

    print(f'build_collection={BUILD_COLLECTION}')
    print(f'output={output_file}')
    print(f'cards={len(cards)}')
    print(f'deck={args.deck}')


if __name__ == '__main__':
    main()
