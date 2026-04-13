#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from anki.collection import Collection

CANONICAL_NOTE_TYPE = 'LeetCode Basic'
VARIANT_PREFIX = f'{CANONICAL_NOTE_TYPE}+'
LEETCODE_TAG_QUERY = 'tag:leetcode'



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



def migrate_variant_notes(col: Collection, variant_name: str) -> tuple[int, int, bool]:
    canonical = col.models.by_name(CANONICAL_NOTE_TYPE)
    variant = col.models.by_name(variant_name)
    if canonical is None:
        raise RuntimeError(f'Canonical note type not found: {CANONICAL_NOTE_TYPE}')
    if variant is None:
        return 0, 0, False

    canonical_field_names = [field['name'] for field in canonical['flds']]
    canonical_template_names = [template['name'] for template in canonical['tmpls']]
    variant_field_names = [field['name'] for field in variant['flds']]

    if canonical_field_names != ['Front', 'Back']:
        raise RuntimeError(f'Canonical note type has unexpected fields: {CANONICAL_NOTE_TYPE}')
    if canonical_template_names != ['Card 1']:
        raise RuntimeError(f'Canonical note type has unexpected templates: {CANONICAL_NOTE_TYPE}')
    if variant_field_names[:2] != ['Front', 'Back']:
        raise RuntimeError(f'Variant note type has unexpected leading fields: {variant_name}')

    note_ids = [
        int(note_id)
        for note_id in col.find_notes(LEETCODE_TAG_QUERY)
        if int(col.get_note(note_id).mid) == int(variant['id'])
    ]

    if note_ids:
        for note_id in note_ids:
            note = col.get_note(note_id)
            for field_index, field_name in enumerate(variant_field_names[2:], start=2):
                if note.fields[field_index].strip():
                    raise RuntimeError(
                        f'Variant note type has non-empty extra field {field_name!r}: {variant_name}'
                    )

        field_map = {field_index: field_index for field_index in range(len(canonical_field_names))}
        field_map.update({field_index: None for field_index in range(len(canonical_field_names), len(variant_field_names))})
        template_map = {0: 0}
        template_map.update({template_index: None for template_index in range(1, len(variant['tmpls']))})
        col.models.change(variant, note_ids, canonical, field_map, template_map)

    removed = False
    if col.models.use_count(variant) == 0:
        col.models.remove(variant['id'])
        removed = True

    return len(note_ids), int(variant['id']), removed



def main() -> None:
    args = parse_args()
    collection_path = Path(args.collection).expanduser().resolve()

    col = Collection(str(collection_path))
    try:
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

        print(f'collection={collection_path}')
        print(f'canonical={CANONICAL_NOTE_TYPE}')
        print(f'variants={len(variant_names)}')
        print(f'migrated_notes={migrated_total}')
        print(f'removed_variants={removed_variants}')
        print(f'variant_model_ids={touched_model_ids}')
    finally:
        col.close()


if __name__ == '__main__':
    main()
