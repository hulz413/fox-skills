"""Rerun original frozen experiment; record HTTP status and stop on 401/403."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
OLD = HERE.with_name('jev-threshold-2026-10-14')
spec = importlib.util.spec_from_file_location('original_trial', OLD / 'run.py')
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
f = old.f


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(name, data):
    with (HERE / name).open('x') as out:
        json.dump(data, out, ensure_ascii=False, indent=2, allow_nan=False)
        out.write('\n')


def verify():
    plan = old.load('plan.json')
    for name, sha in plan['hashes']['local'].items():
        assert digest(OLD / name) == sha, name
    for name, sha in plan['hashes']['protected'].items():
        assert digest(old.ROOT / name) == sha, name
    cases = {c['id']: c for c in old.samples()}
    assert plan['requests'] == {cid:f.make_request(c['state']) for cid,c in cases.items()}
    assert f.MODEL == plan['model'] == 'jev-1.13.0'
    assert f.DROP_THRESHOLD == plan['runtime_threshold'] == .99
    assert plan['candidate_thresholds'] == old.THRESHOLDS == [.90,.95,.97,.99]
    return plan, cases


def freeze():
    plan, _ = verify()
    save('manifest.json', {
        'created_at':datetime.now(timezone.utc).isoformat(),
        'original_plan_sha256':digest(OLD/'plan.json'),
        'original_files':{str(p.relative_to(OLD)):digest(p) for p in OLD.rglob('*') if p.is_file() and '__pycache__' not in p.parts},
        'runner_sha256':digest(HERE/'run.py'),
        'total_attempts_unless_auth_failure':48, 'auth_stop_statuses':[401,403],
        'retries':0, 'additional_probe_calls':0,
        'policy':'Original requests, order, labels, split, candidates and selection/scoring functions unchanged. Lock selection before holdout. Auth failure aborts immediately; no replacement calls. HTTP statuses are recorded without headers or bodies.'})
    print('Frozen round 2 manifest; no API calls.')


class AuthStop(Exception):
    pass


def transport(payload, key, metadata):
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args): return None
    request = urllib.request.Request(f.ENDPOINT, data=f.encode(payload), headers={
        'Authorization':'Bearer '+key, 'Content-Type':'application/json'})
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=20) as response:
            metadata['http_status'] = response.status
            raw = response.read(1_000_001)
            if len(raw)>1_000_000: raise ValueError('oversized response')
            return json.loads(raw)
    except urllib.error.HTTPError as error:
        metadata['http_status'] = error.code
        error.close()
        raise


def collect(split, plan, cases, records, selection_hash=None):
    rows = []
    with (HERE/f'{split}.jsonl').open('x') as out:
        for trial, entry in enumerate(plan['orders'][split],1):
            metadata={'http_status':None}
            captured=[]
            def evaluate(payload,key):
                assert payload == plan['requests'][entry['case_id']]
                response = transport(payload,key,metadata)
                captured.append(response)
                return response
            result=f.filter_context(cases[entry['case_id']]['state'],key=os.environ['TYPESAFE_API_KEY'],evaluate=evaluate)
            row={'split':split,'trial':trial,**entry,**metadata,
                 'original_plan_sha256':digest(OLD/'plan.json'),
                 'selection_sha256':selection_hash,
                 'request_sha256':hashlib.sha256(f.encode(plan['requests'][entry['case_id']])).hexdigest(),
                 'result':{k:v for k,v in result.items() if k not in ('goal','fragments')}}
            if captured: row['response']=captured[0]
            out.write(json.dumps(row,ensure_ascii=False,allow_nan=False)+'\n');out.flush()
            rows.append(row);records.append(row)
            print(f"{split} {trial}/24 {entry['case_id']} HTTP={metadata['http_status']} {result['status']}",flush=True)
            if metadata['http_status'] in (401,403): raise AuthStop()
    return rows


def run():
    if not os.environ.get('TYPESAFE_API_KEY'): raise SystemExit('Missing credential')
    if any((HERE/n).exists() for n in ('calibration.jsonl','holdout.jsonl','selection.json','summary.json')):
        raise SystemExit('Existing results; refusing additional calls')
    plan,cases=verify()
    manifest=json.loads((HERE/'manifest.json').read_text())
    assert digest(HERE/'run.py')==manifest['runner_sha256']
    assert digest(OLD/'plan.json')==manifest['original_plan_sha256']
    assert all(digest(OLD/n)==h for n,h in manifest['original_files'].items())
    records=[]; summary={'status':'completed','accepted':False}
    try:
        calibration=collect('calibration',plan,cases,records)
        selection=old.choose(calibration,cases)
        selection.update(locked_at=datetime.now(timezone.utc).isoformat(),
                         calibration_sha256=digest(HERE/'calibration.jsonl'))
        save('selection.json',selection)
        selection_hash=digest(HERE/'selection.json')
        print('SELECTION LOCKED:',selection['selected_threshold'],flush=True)
        heldout=collect('holdout',plan,cases,records,selection_hash)
        metrics=old.score(heldout,cases,selection['selected_threshold'])
        summary.update(selected_threshold=selection['selected_threshold'],
                       selection_sha256=selection_hash,holdout=metrics,
                       holdout_keep_all=old.score(heldout,cases,None),
                       accepted=selection['selected_threshold'] is not None and metrics['eligible'] and metrics['useful_in_both_repeats'])
        assert digest(HERE/'selection.json')==selection_hash
    except AuthStop:
        summary.update(status='stopped_auth_failure',stop_http_status=records[-1]['http_status'])
    summary.update(attempts=len(records),valid_responses=sum(r['result']['status']=='ok' for r in records),
                   unknown_usage_responses=sum(r['result']['usage'] is None for r in records),
                   known_usage={k:sum(r['result']['usage'][k] for r in records if r['result']['usage']) for k in ('input_tokens','output_tokens')},
                   request_latency_seconds=sum(r['result']['latency_seconds'] for r in records))
    verify()
    assert all(digest(OLD/n)==h for n,h in manifest['original_files'].items())
    save('summary.json',summary)
    print(json.dumps(summary,ensure_ascii=False),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true')
    args=parser.parse_args()
    run() if args.run else freeze()
