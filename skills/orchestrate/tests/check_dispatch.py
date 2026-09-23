"""Check actual Codex rollout calls for the bounded routing smoke scenario.

This scenario has self-contained assignments, so inheritance is not an exception.
Model IDs are supplied by the evaluator from the runtime catalog, never pinned here.
"""
import argparse
import json
from pathlib import Path


def dispatches(path):
    for line in Path(path).read_text().splitlines():
        record = json.loads(line)
        payload = record.get('payload', {})
        if (record.get('type') == 'response_item'
                and payload.get('type') == 'function_call'
                and payload.get('name', '').split('.')[-1] == 'spawn_agent'):
            yield json.loads(payload['arguments'])


def check(calls, efficient_models):
    errors = []
    if len(calls) != 2:
        errors.append(f'Expected two bounded worker dispatches, got {len(calls)}')
    for i, call in enumerate(calls, 1):
        for key in ('model', 'reasoning_effort'):
            if not isinstance(call.get(key), str) or not call[key].strip():
                errors.append(f'Dispatch {i}: missing explicit {key}')
        fork = call.get('fork_turns', 'all')
        if not (fork == 'none' or (isinstance(fork, str) and fork.isdigit() and int(fork) > 0)):
            errors.append(f'Dispatch {i}: full-history fork prevents overrides')
        if call.get('model') not in efficient_models:
            errors.append(f'Dispatch {i}: expected an efficient model for this simple assignment')
    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rollout', type=Path)
    parser.add_argument('--efficient-model', action='append', required=True)
    args = parser.parse_args()
    errors = check(list(dispatches(args.rollout)), set(args.efficient_model))
    print('\n'.join(errors) if errors else 'PASS: explicit efficient-model dispatches with compatible context modes')
    raise SystemExit(bool(errors))
