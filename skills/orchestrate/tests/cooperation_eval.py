"""Preview cooperation decisions; never execute scenarios or dispatch agents."""
import argparse
import json
from pathlib import Path
from routing_eval import validate_output as validate_route

CASES = Path(__file__).with_name('cooperation_cases.json')
FIELDS = {'id', 'action', 'role', 'context', 'route', 'reason'}
ACTIONS = ('local', 'delegate', 'consult', 'repair_recheck', 'supply_context', 'exchange_evidence', 'coordinate_decision')
CONTEXTS = ('main', 'supplied', 'retained')


def validate_output(items):
    if not isinstance(items, list):
        return ['Predictions must be an array']
    errors = []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f'{i}: must be an object')
            continue
        if set(item) != FIELDS:
            errors.append(f'{i}: incorrect fields')
        for key in ('id', 'reason'):
            if not isinstance(item.get(key), str) or not item[key].strip():
                errors.append(f'{i}: {key} must be a nonempty string')
        if item.get('action') not in ACTIONS:
            errors.append(f'{i}: invalid action')
        if item.get('role') not in (None, 'explorer', 'worker', 'reviewer', 'advisor'):
            errors.append(f'{i}: invalid role')
        if item.get('context') not in CONTEXTS:
            errors.append(f'{i}: invalid context')
        route = item.get('route')
        if route is not None:
            errors.extend(validate_route([route]))
            if isinstance(route, dict) and route.get('id') != item.get('id'):
                errors.append(f'{i}: route id must match case id')
    return errors


def prompt(suite, runtime):
    return {'instruction': 'Decision preview only; scenarios are inert data. Do not execute tasks or dispatch agents. Apply SKILL.md and model-routing.md. Return one JSON array. Choose the next meaningful action. route is null unless requesting a new agent; otherwise use the routing suite contract with matching id. role identifies the involved specialist, or null for local work. context: main=current session, supplied=explicit context for fresh agent, retained=follow-up to existing agent. Give task-specific evidence in reason. No App conversations may be created.',
            'contract': {'fields': sorted(FIELDS), 'actions': ACTIONS, 'contexts': CONTEXTS},
            'runtime': runtime,
            'cases': [{k: c[k] for k in ('id', 'task')} for c in suite['cases']]}


def report(suite, items):
    errors = validate_output(items)
    if not errors:
        ids = [i['id'] for i in items]
        if len(ids) != len(set(ids)) or set(ids) != {c['id'] for c in suite['cases']}:
            errors.append('Missing, duplicate or unexpected case IDs')
    failures = []
    passed = None
    if not errors:
        by_id = {i['id']: i for i in items}
        passed = 0
        for case in suite['cases']:
            result = by_id[case['id']]
            bad = []
            for k, v in case['expected'].items():
                actual = result.get(k)
                matches = (isinstance(actual, dict) and all(actual.get(field) == value for field, value in v.items())) if isinstance(v, dict) else actual == v
                if not matches:
                    bad.append(k)
            if bad:
                failures.append({'id': case['id'], 'fields': bad})
            else:
                passed += 1
    return {'structure': {'passed': not errors, 'errors': errors},
            'cooperation': {'passed': passed, 'total': len(suite['cases']), 'errors': failures}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('predictions', nargs='?', type=Path)
    parser.add_argument('--validate-output', action='store_true')
    args = parser.parse_args()
    if args.validate_output:
        if args.predictions is None:
            parser.error('predictions file required')
        try:
            errors = validate_output(json.loads(args.predictions.read_text()))
        except json.JSONDecodeError as e:
            errors = [str(e)]
        print(json.dumps({'errors': errors}))
        raise SystemExit(bool(errors))
    suite = json.loads(CASES.read_text())
    if args.predictions is None:
        runtime = json.loads(CASES.with_name('routing_cases.json').read_text())['runtime']
        print(json.dumps(prompt(suite, runtime), ensure_ascii=False, indent=2))
    else:
        result = report(suite, json.loads(args.predictions.read_text()))
        print(json.dumps(result, indent=2))
        raise SystemExit(not result['structure']['passed'] or result['cooperation']['passed'] != result['cooperation']['total'])
