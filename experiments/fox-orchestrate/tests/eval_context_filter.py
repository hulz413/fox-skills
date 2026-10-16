"""Explicit live smoke test on synthetic evidence; exactly one request, no retries."""
import json
import os
from pathlib import Path
from test_filter_context import f

if __name__ == '__main__':
    data = json.loads(Path(__file__).with_name('context_filter_case.json').read_text())
    captured = []
    attempts = []
    def evaluate(payload, key):
        attempts.append(True)
        response = f.call_api(payload, key)
        captured.append(response)
        return response
    shadow = f.filter_context(data, key=os.environ.get('TYPESAFE_API_KEY'), evaluate=evaluate)
    applied = f.filter_context(data, apply=True, key='replay', evaluate=lambda *_: captured[0]) if captured else shadow
    kept = {item['id'] for item in applied['fragments']}
    required = {'constraints', 'failure', 'counter', 'dependency', 'ambiguous', 'injection'}
    report = {'fixture': 'context_filter_case.json', 'requests': len(attempts),
              'shadow': {k: v for k, v in shadow.items() if k not in ('goal', 'fragments')},
              'replayed_apply_kept_ids': sorted(kept),
              'checks': {'service_ok': shadow['status'] == 'ok',
                         'shadow_preserves_all': shadow['fragments'] == data['fragments'],
                         'critical_evidence_preserved': required <= kept,
                         'unrelated_noise_removed': 'noise' not in kept},
              'baseline_text_bytes': sum(len(x['text'].encode()) for x in data['fragments']),
              'filtered_text_bytes': sum(len(x['text'].encode()) for x in applied['fragments'])}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if all(report['checks'].values()) else 1)
