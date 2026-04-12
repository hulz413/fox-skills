#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from anki.collection import Collection

DEFAULT_MAIN_COLLECTION = Path('~/Library/Application Support/Anki2/User 1/collection.anki2').expanduser()
CANONICAL_DECK = 'LeetCode'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Merge LeetCode-related edge-case decks into the canonical LeetCode deck.')
    parser.add_argument(
        '--collection',
        default=str(DEFAULT_MAIN_COLLECTION),
        help='Path to the main Anki collection.',
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    collection_path = Path(args.collection).expanduser().resolve()

    col = Collection(str(collection_path))
    try:
        canonical_id = col.decks.id_for_name(CANONICAL_DECK)
        if canonical_id is None:
            print('canonical-deck-missing')
            return

        moved_cards = 0
        removed_decks: list[int] = []

        for deck in col.decks.all():
            if deck['id'] == canonical_id:
                continue
            if deck['name'] != CANONICAL_DECK and not deck['name'].startswith(f'{CANONICAL_DECK}::'):
                continue

            child_ids = list(col.decks.deck_and_child_ids(deck['id']))
            card_ids: list[int] = []
            for deck_id in child_ids:
                deck_info = col.decks.get(deck_id, default=False)
                if not deck_info:
                    continue
                query = f'deck:"{deck_info["name"]}"'
                card_ids.extend(int(card_id) for card_id in col.find_cards(query))

            if card_ids:
                col.set_deck(card_ids, canonical_id)
                moved_cards += len(card_ids)

            col.decks.remove(child_ids)
            removed_decks.extend(child_ids)

        col.save()
        print(f'collection={collection_path}')
        print(f'canonical-deck={canonical_id}')
        print(f'moved-cards={moved_cards}')
        print(f'removed-decks={len(removed_decks)}')
    finally:
        col.close()


if __name__ == '__main__':
    main()
