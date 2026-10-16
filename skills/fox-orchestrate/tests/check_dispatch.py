"""Check actual Codex rollout calls for the bounded routing smoke scenario.

This scenario has self-contained assignments, so inheritance is not an exception.
Model IDs are supplied by the evaluator from the runtime catalog, never pinned here.
"""
import argparse
import json
from pathlib import Path
from routing_eval import valid_context_mode


def dispatches(path, task_names=None):
    with Path(path).open() as source:
        for line in source:
            record = json.loads(line)
            payload = record.get('payload', {})
            if (record.get('type') == 'response_item'
                    and payload.get('type') == 'function_call'
                    and payload.get('name', '').split('.')[-1] in ('spawn_agent', 'start_delegated_task')):
                arguments = payload['arguments']
                call = json.loads(arguments) if isinstance(arguments, str) else arguments
                if task_names is None or (isinstance(call, dict)
                                         and isinstance(call.get('task_name'), str)
                                         and call['task_name'] in task_names):
                    yield call


def check(calls, efficient_models, expected=None):
    errors = []
    count = len(expected) if expected is not None else 2
    if len(calls) != count:
        errors.append(f'Expected {count} bounded worker dispatches, got {len(calls)}')
    if expected is not None:
        names = [call.get('task_name') for call in calls if isinstance(call, dict)]
        if any(names.count(name) != 1 for name in expected) or any(
                not isinstance(name, str) or name not in expected for name in names):
            errors.append('Missing, duplicate or unexpected assignment names')
    for i, call in enumerate(calls, 1):
        if not isinstance(call, dict):
            errors.append(f'Dispatch {i}: must be an object')
            continue
        for key in ('model', 'reasoning_effort'):
            if not isinstance(call.get(key), str) or not call[key].strip():
                errors.append(f'Dispatch {i}: missing explicit {key}')
        fork = call.get('fork_turns', 'all')
        if fork == 'all' or not valid_context_mode(fork):
            errors.append(f'Dispatch {i}: full-history fork prevents overrides')
        if isinstance(call.get('model'), str) and call['model'] not in efficient_models:
            errors.append(f'Dispatch {i}: expected an efficient model for this simple assignment')
        if expected is not None and isinstance(call.get('task_name'), str):
            route = expected.get(call['task_name'], {})
            for key, value in route.items():
                if call.get(key) != value:
                    errors.append(f'Dispatch {i}: {key} differs from the selected route')
    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rollout', type=Path)
    parser.add_argument('--efficient-model', action='append', required=True)
    parser.add_argument('--expectations', type=Path,
                        help='JSON mapping of assignment names to selected model, effort and context')
    args = parser.parse_args()
    expected = json.loads(args.expectations.read_text()) if args.expectations else None
    if expected is not None and (not isinstance(expected, dict) or not expected or any(
            not isinstance(name, str) or not name or not isinstance(route, dict)
            or set(route) != {'model', 'reasoning_effort', 'fork_turns'}
            or any(not isinstance(value, str) or not value for value in route.values())
            for name, route in expected.items())):
        parser.error('expectations require named model/effort/context routes')
    errors = check(list(dispatches(args.rollout, expected)), set(args.efficient_model), expected)
    print('\n'.join(errors) if errors else 'PASS: explicit efficient-model dispatches with compatible context modes')
    raise SystemExit(bool(errors))
