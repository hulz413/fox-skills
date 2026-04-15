#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from anki.collection import Collection

CANONICAL_NOTE_TYPE = 'LeetCode Basic'
VARIANT_PREFIX = f'{CANONICAL_NOTE_TYPE}+'
LEETCODE_TAG_QUERY = 'tag:leetcode'
STOCK_NOTE_TYPE = 'Basic'
EXPECTED_FIELD_NAMES = ['Front', 'Back']
EXPECTED_TEMPLATE_NAMES = ['Card 1']
EXPECTED_BASIC_STOCK_KIND = 1



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Normalize LeetCode Basic note type variants back to the canonical LeetCode Basic note type.',
    )
    parser.add_argument(
        '--collection',
        required=True,
        help='Path to the Anki collection to normalize.',
    )
    return parser.parse_args()



def note_ids_for_model(col: Collection, model_id: int) -> list[int]:
    return [
        int(note_id)
        for note_id in col.find_notes(LEETCODE_TAG_QUERY)
        if int(col.get_note(note_id).mid) == int(model_id)
    ]



def validate_basic_compatible_model(model: dict[str, Any], model_name: str) -> tuple[list[str], list[str]]:
    field_names = [field['name'] for field in model['flds']]
    template_names = [template['name'] for template in model['tmpls']]
    stock_kind = model.get('originalStockKind')

    if field_names[:2] != EXPECTED_FIELD_NAMES:
        raise RuntimeError(f'Note type has unexpected leading fields: {model_name}')
    if template_names[:1] != EXPECTED_TEMPLATE_NAMES:
        raise RuntimeError(f'Note type has unexpected leading templates: {model_name}')
    if stock_kind != EXPECTED_BASIC_STOCK_KIND:
        raise RuntimeError(f'Note type has unexpected kind: {model_name}')

    return field_names, template_names



def create_canonical_from_stock(col: Collection) -> dict[str, Any]:
    stock_model = col.models.by_name(STOCK_NOTE_TYPE)
    if stock_model is None:
        raise RuntimeError(f'Stock note type not found: {STOCK_NOTE_TYPE}')

    stock_field_names = [field['name'] for field in stock_model['flds']]
    stock_template_names = [template['name'] for template in stock_model['tmpls']]
    stock_kind = stock_model.get('originalStockKind')
    if stock_field_names != EXPECTED_FIELD_NAMES:
        raise RuntimeError(f'Stock note type has unexpected fields: {STOCK_NOTE_TYPE}')
    if stock_template_names != EXPECTED_TEMPLATE_NAMES:
        raise RuntimeError(f'Stock note type has unexpected templates: {STOCK_NOTE_TYPE}')
    if stock_kind != EXPECTED_BASIC_STOCK_KIND:
        raise RuntimeError(f'Stock note type has unexpected kind: {STOCK_NOTE_TYPE}')

    cloned_model = col.models.copy(stock_model, add=False)
    cloned_model['name'] = CANONICAL_NOTE_TYPE
    col.models.add(cloned_model)
    canonical = col.models.by_name(CANONICAL_NOTE_TYPE)
    if canonical is None:
        raise RuntimeError(f'Failed to create canonical note type: {CANONICAL_NOTE_TYPE}')
    return canonical



def ensure_canonical_note_type(col: Collection) -> tuple[dict[str, Any], bool, int, int]:
    canonical = col.models.by_name(CANONICAL_NOTE_TYPE)
    created = False
    if canonical is None:
        canonical = create_canonical_from_stock(col)
        created = True

    field_names, template_names = validate_basic_compatible_model(canonical, CANONICAL_NOTE_TYPE)
    note_ids = note_ids_for_model(col, int(canonical['id']))

    extra_templates_removed = 0
    if len(template_names) > len(EXPECTED_TEMPLATE_NAMES):
        for template in list(reversed(canonical['tmpls'][len(EXPECTED_TEMPLATE_NAMES):])):
            col.models.remove_template(canonical, template)
            extra_templates_removed += 1

    extra_fields_removed = 0
    if len(field_names) > len(EXPECTED_FIELD_NAMES):
        for note_id in note_ids:
            note = col.get_note(note_id)
            for field_index, field_name in enumerate(field_names[len(EXPECTED_FIELD_NAMES):], start=len(EXPECTED_FIELD_NAMES)):
                if note.fields[field_index].strip():
                    raise RuntimeError(
                        f'Canonical note type has non-empty extra field {field_name!r}: {CANONICAL_NOTE_TYPE}'
                    )

        for field in list(reversed(canonical['flds'][len(EXPECTED_FIELD_NAMES):])):
            col.models.remove_field(canonical, field)
            extra_fields_removed += 1

    if extra_templates_removed or extra_fields_removed:
        col.models.update_dict(canonical)
        canonical = col.models.by_name(CANONICAL_NOTE_TYPE)
        if canonical is None:
            raise RuntimeError(f'Canonical note type disappeared: {CANONICAL_NOTE_TYPE}')

    return canonical, created, extra_templates_removed, extra_fields_removed



def migrate_variant_notes(col: Collection, variant_name: str) -> tuple[int, int, bool]:
    canonical, _, _, _ = ensure_canonical_note_type(col)
    variant = col.models.by_name(variant_name)
    if variant is None:
        return 0, 0, False

    canonical_field_names, canonical_template_names = validate_basic_compatible_model(canonical, CANONICAL_NOTE_TYPE)
    variant_field_names, variant_template_names = validate_basic_compatible_model(variant, variant_name)

    note_ids = note_ids_for_model(col, int(variant['id']))

    if note_ids:
        for note_id in note_ids:
            note = col.get_note(note_id)
            for field_index, field_name in enumerate(variant_field_names[len(canonical_field_names):], start=len(canonical_field_names)):
                if note.fields[field_index].strip():
                    raise RuntimeError(
                        f'Variant note type has non-empty extra field {field_name!r}: {variant_name}'
                    )

        field_map = {field_index: field_index for field_index in range(len(canonical_field_names))}
        field_map.update(
            {field_index: None for field_index in range(len(canonical_field_names), len(variant_field_names))}
        )
        template_map = {template_index: template_index for template_index in range(len(canonical_template_names))}
        template_map.update(
            {template_index: None for template_index in range(len(canonical_template_names), len(variant_template_names))}
        )
        col.models.change(variant, note_ids, canonical, field_map, template_map)

    removed = False
    if col.models.use_count(variant) == 0:
        col.models.remove(variant['id'])
        removed = True

    return len(note_ids), int(variant['id']), removed



def remove_duplicate_cards(col: Collection, model_id: int) -> int:
    removed_cards = 0
    for note_id in note_ids_for_model(col, model_id):
        card_ids = sorted(int(card_id) for card_id in col.card_ids_of_note(note_id))
        if len(card_ids) <= 1:
            continue

        ord_zero_cards: list[int] = []
        other_cards: list[int] = []
        for card_id in card_ids:
            card = col.get_card(card_id)
            if int(card.ord) == 0:
                ord_zero_cards.append(card_id)
            else:
                other_cards.append(card_id)

        if ord_zero_cards:
            keep_card = ord_zero_cards[0]
            remove_ids = other_cards + ord_zero_cards[1:]
        else:
            keep_card = card_ids[0]
            remove_ids = card_ids[1:]

        if keep_card and remove_ids:
            col.remove_cards_and_orphaned_notes(remove_ids)
            removed_cards += len(remove_ids)

    return removed_cards



def main() -> None:
    args = parse_args()
    collection_path = Path(args.collection).expanduser().resolve()

    col = Collection(str(collection_path))
    try:
        canonical, created_canonical, extra_templates_removed, extra_fields_removed = ensure_canonical_note_type(col)
        variant_names = [
            model.name
            for model in col.models.all_names_and_ids()
            if model.name == VARIANT_PREFIX or model.name.startswith(VARIANT_PREFIX)
        ]
        migrated_total = 0
        touched_model_ids: list[int] = []
        removed_variants = 0
        for variant_name in variant_names:
            migrated_count, model_id, removed = migrate_variant_notes(col, variant_name)
            migrated_total += migrated_count
            if model_id:
                touched_model_ids.append(model_id)
            if removed:
                removed_variants += 1

        canonical = col.models.by_name(CANONICAL_NOTE_TYPE)
        if canonical is None:
            raise RuntimeError(f'Canonical note type not found after migration: {CANONICAL_NOTE_TYPE}')
        removed_duplicate_cards = remove_duplicate_cards(col, int(canonical['id']))

        print(f'collection={collection_path}')
        print(f'canonical={CANONICAL_NOTE_TYPE}')
        print(f'created_canonical={created_canonical}')
        print(f'variants={len(variant_names)}')
        print(f'migrated_notes={migrated_total}')
        print(f'removed_variants={removed_variants}')
        print(f'removed_extra_templates={extra_templates_removed}')
        print(f'removed_extra_fields={extra_fields_removed}')
        print(f'removed_duplicate_cards={removed_duplicate_cards}')
        print(f'variant_model_ids={touched_model_ids}')
    finally:
        col.close()



if __name__ == '__main__':
    main()
