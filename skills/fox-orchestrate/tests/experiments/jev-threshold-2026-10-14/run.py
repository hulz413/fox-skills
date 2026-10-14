"""Frozen threshold calibration and held-out validation; --run makes 48 calls."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('filter_context', ROOT / 'scripts/filter_context.py')
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)
THRESHOLDS = [0.90, 0.95, 0.97, 0.99]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name):
    return json.loads((HERE / name).read_text())


def write_once(name, data):
    with (HERE / name).open('x') as out:
        json.dump(data, out, ensure_ascii=False, indent=2, allow_nan=False)
        out.write('\n')


def samples():
    data = load('samples.json')
    assert len(data) == 24 and len({c['id'] for c in data}) == 24
    assert Counter((c['split'], c['category']) for c in data) == Counter({
        (s, k): 3 for s in ('calibration', 'holdout') for k in ('logs', 'code', 'docs', 'handoff')})
    source_sets = {'calibration': set(), 'holdout': set()}
    for c in data:
        f.validate(c['state'])
        assert len(c['state']['fragments']) == 7
        assert set(c['annotations']) == {x['id'] for x in c['state']['fragments']}
        assert Counter(a['label'] for a in c['annotations'].values()) == Counter(
            required=1, critical=3, uncertain=1, drop=2)
        for item in c['state']['fragments']:
            annotation = c['annotations'][item['id']]
            assert item['required'] == (annotation['label'] == 'required')
            if annotation['provenance'] == 'repository_excerpt':
                source_sets[c['split']].add(item['source'].split(':')[0])
        assert len(f.encode(f.make_request(c['state']))) <= f.MAX_REQUEST_BYTES
    assert not source_sets['calibration'] & source_sets['holdout'], 'cross-split source file leak'
    return data


def current_hashes():
    protected = {str(p.relative_to(ROOT)): digest(p) for p in sorted(ROOT.rglob('*'))
                 if p.is_file() and HERE not in p.parents and '__pycache__' not in p.parts}
    return {'protected': protected, 'local': {n: digest(HERE / n) for n in (
        'samples.json', 'build_samples.py', 'run.py', 'PROTOCOL.md')}}


def verify_plan(plan):
    assert f.MODEL == plan['model'] == 'jev-1.13.0'
    assert f.DROP_THRESHOLD == plan['runtime_threshold'] == 0.99
    assert plan['candidate_thresholds'] == THRESHOLDS
    assert current_hashes() == plan['hashes'], 'Frozen files changed'
    data = samples()
    requests = {c['id']: f.make_request(c['state']) for c in data}
    assert requests == plan['requests']
    return {c['id']: c for c in data}


def prepare():
    data = samples()
    rng = random.Random(2026101402)
    orders = {}
    for split in ('calibration', 'holdout'):
        ids = [c['id'] for c in data if c['split'] == split]
        orders[split] = []
        for repeat in (1, 2):
            order = ids.copy()
            rng.shuffle(order)
            orders[split].extend({'case_id': cid, 'repeat': repeat} for cid in order)
    plan = {'created_at': datetime.now(timezone.utc).isoformat(), 'model': f.MODEL,
            'runtime_threshold': f.DROP_THRESHOLD, 'candidate_thresholds': THRESHOLDS,
            'requests_per_split': 24, 'total_requests': 48, 'retries': 0,
            'orders': orders, 'hashes': current_hashes(),
            'requests': {c['id']: f.make_request(c['state']) for c in data}}
    verify_plan(plan)
    write_once('plan.json', plan)
    print('Frozen 24 cases, 168 labels, 48 calls; no network.')


def score(rows, cases, threshold):
    out = {'threshold': threshold, 'service_failures': 0, 'critical_dropped': [],
           'uncertain_dropped': [], 'required_dropped': [], 'noise_dropped': 0,
           'noise_total': 0, 'correct_removed_text_bytes': 0,
           'baseline_text_bytes': 0, 'removed_text_bytes': 0,
           'repeats': {str(r): {'noise_dropped': 0, 'noise_total': 0} for r in (1, 2)}}
    decisions = {}
    for row in rows:
        case = cases[row['case_id']]
        valid = row['result']['status'] == 'ok'
        if not valid:
            out['service_failures'] += 1
        for item in case['state']['fragments']:
            label = case['annotations'][item['id']]['label']
            drop = (valid and threshold is not None and not item['required']
                    and row['result']['judgments'][item['id']] >= threshold)
            size = len(item['text'].encode())
            out['baseline_text_bytes'] += size
            if drop:
                out['removed_text_bytes'] += size
            key = (row['case_id'], item['id'])
            decisions.setdefault(key, []).append(drop)
            if label == 'drop':
                out['noise_total'] += 1
                out['repeats'][str(row['repeat'])]['noise_total'] += 1
                if drop:
                    out['noise_dropped'] += 1
                    out['correct_removed_text_bytes'] += size
                    out['repeats'][str(row['repeat'])]['noise_dropped'] += 1
            elif drop:
                out[label + '_dropped'].append({'case_id': row['case_id'], 'id': item['id'],
                                               'repeat': row['repeat'],
                                               'p': row['result']['judgments'][item['id']]})
    out['unstable_fragments'] = sum(len(set(values)) > 1 for values in decisions.values())
    out['eligible'] = (len(rows) == 24 and out['service_failures'] == 0 and
                       not any(out[k] for k in ('critical_dropped', 'uncertain_dropped', 'required_dropped')))
    out['useful_in_both_repeats'] = all(r['noise_dropped'] > 0 for r in out['repeats'].values())
    return out


def choose(rows, cases):
    metrics = [score(rows, cases, t) for t in THRESHOLDS]
    eligible = [m for m in metrics if m['eligible'] and m['useful_in_both_repeats']]
    def rank(m):
        return (min(r['noise_dropped'] for r in m['repeats'].values()), m['noise_dropped'],
                m['correct_removed_text_bytes'], -m['unstable_fragments'], m['threshold'])
    best = max(eligible, key=rank) if eligible else None
    return {'selected_threshold': best['threshold'] if best else None,
            'reason': 'ranked_safe_useful_candidate' if best else 'no_safe_useful_candidate',
            'metrics': metrics, 'keep_all_baseline': score(rows, cases, None)}


def collect(split, plan, cases):
    rows = []
    key = os.environ['TYPESAFE_API_KEY']
    with (HERE / f'{split}.jsonl').open('x') as output:
        for trial, entry in enumerate(plan['orders'][split], 1):
            case = cases[entry['case_id']]
            captured = []
            def evaluate(payload, credential):
                assert payload == plan['requests'][entry['case_id']]
                response = f.call_api(payload, credential)
                captured.append(response)
                return response
            result = f.filter_context(case['state'], key=key, evaluate=evaluate)
            row = {'split': split, 'trial': trial, **entry, 'plan_sha256': digest(HERE / 'plan.json'),
                   'request_sha256': hashlib.sha256(f.encode(plan['requests'][entry['case_id']])).hexdigest(),
                   'result': {k: v for k, v in result.items() if k not in ('goal', 'fragments')}}
            if captured:
                row['response'] = captured[0]
            output.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n')
            output.flush()
            rows.append(row)
            print(f"{split} {trial}/24 {entry['case_id']} repeat={entry['repeat']} {result['status']}", flush=True)
    return rows


def run():
    if not os.environ.get('TYPESAFE_API_KEY'):
        raise SystemExit('Missing TYPESAFE_API_KEY')
    for name in ('calibration.jsonl', 'selection.json', 'holdout.jsonl', 'summary.json'):
        if (HERE / name).exists():
            raise SystemExit('Results already exist; refusing any additional calls.')
    plan = load('plan.json')
    plan_hash = digest(HERE / 'plan.json')
    cases = verify_plan(plan)
    calibration = collect('calibration', plan, cases)
    selection = choose(calibration, cases)
    selection.update(calibration_sha256=digest(HERE / 'calibration.jsonl'),
                     plan_sha256=plan_hash, locked_at=datetime.now(timezone.utc).isoformat())
    write_once('selection.json', selection)
    selection_hash = digest(HERE / 'selection.json')
    print('SELECTION LOCKED:', selection['selected_threshold'], flush=True)
    heldout = collect('holdout', plan, cases)
    threshold = selection['selected_threshold']
    heldout_metrics = score(heldout, cases, threshold)
    summary = {'plan_sha256': plan_hash, 'selection_sha256': selection_hash,
               'calibration': selection,
               'holdout_at_locked_policy': heldout_metrics,
               'holdout_keep_all_baseline': score(heldout, cases, None),
               'accepted': threshold is not None and heldout_metrics['eligible']
                           and heldout_metrics['useful_in_both_repeats'],
               'calls': len(calibration) + len(heldout),
               'usage': {k: sum(r['result']['usage'][k] for r in calibration + heldout
                                if r['result']['usage']) for k in ('input_tokens', 'output_tokens')},
               'request_latency_seconds': sum(r['result']['latency_seconds'] for r in calibration + heldout)}
    verify_plan(plan)
    assert digest(HERE / 'plan.json') == plan_hash and digest(HERE / 'selection.json') == selection_hash
    write_once('summary.json', summary)
    print('COMPLETE accepted=', summary['accepted'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    run() if args.run else prepare()
