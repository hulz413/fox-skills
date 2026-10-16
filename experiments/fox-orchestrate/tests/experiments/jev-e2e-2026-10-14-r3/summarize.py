"""Summarize preregistered quality and actual usage; never price subscription tokens."""
import json,statistics,hashlib
from pathlib import Path
import run
HERE=Path(__file__).resolve().parent

def main():
 run.verify()
 calls=[json.loads(x) for x in (HERE/'calls.jsonl').read_text().splitlines()]
 rows=[json.loads(x) for x in (HERE/'results.jsonl').read_text().splitlines()] if (HERE/'results.jsonl').exists() else []
 keys=('input_tokens','cached_input_tokens','cache_write_input_tokens','output_tokens','reasoning_output_tokens')
 def usage_sum(us):return {k:sum(u.get(k,0) for u in us if u) for k in keys}
 physical={b:{'calls':sum(c['backend']==b for c in calls),'seconds':sum(c['seconds'] for c in calls if c['backend']==b),'usage':usage_sum([c.get('usage') if b=='codex_cli' else (c.get('response') or {}).get('usage') for c in calls if c['backend']==b])} for b in ('codex_cli','typesafe')}
 mapping=run.load('review-mapping.json') if (HERE/'review-mapping.json').exists() else {}
 grades=run.load('review-scores.json') if (HERE/'review-scores.json').exists() else []
 bykey={tuple(mapping[g['review_id']][k] for k in ('case','repeat','arm')):g for g in grades}
 cases={c['id']:c for c in run.load('samples.json')}
 for g in grades:
  case=cases[mapping[g['review_id']]['case']]
  assert len(g['facts'])==len(case['rubric']) and all(v in (0,1) for v in g['facts'])
  assert set(g)>= {'review_id','facts','critical_issue','unsupported_claim','citations_supported','complete','notes'}
 groups={};regressions=[]
 for split in ('calibration','holdout'):
  groups[split]={}
  for arm in ('A','B'):
   rs=[r for r in rows if (r['split'],r['arm'])==(split,arm)]
   if not rs:continue
   gs=[bykey[(r['case'],r['repeat'],arm)] for r in rs if (r['case'],r['repeat'],arm) in bykey]
   ju=[(c.get('response') or {}).get('usage') for c in calls if c['backend']=='typesafe' and (c['split'],c['arm'])==(split,arm)]
   groups[split][arm]={'runs':len(rs),'generator_usage_allocated':usage_sum([u for r in rs for u in [r['query_usage_allocated']]+r['answer_usage']]),
    'jev_usage':usage_sum(ju),'reader_rounds':sum(r['rounds'] for r in rs),'mean_seconds':statistics.mean(r['seconds'] for r in rs),
    'read_units':sum(len(r['selected']) for r in rs),'graded':len(gs),
    'complete_supported_answers':sum(g['complete'] and not g['critical_issue'] and not g['unsupported_claim'] and g['citations_supported'] and all(g['facts']) for g in gs),
    'macro_fact_coverage':statistics.mean(sum(g['facts'])/len(g['facts']) for g in gs) if gs else None}
 for r in rows:
  if r['split']!='holdout' or r['arm']!='B':continue
  a=bykey.get((r['case'],r['repeat'],'A'));b=bykey.get((r['case'],r['repeat'],'B'))
  if not a or not b:continue
  lost_critical=any(f['critical'] and av and not bv for f,av,bv in zip(cases[r['case']]['rubric'],a['facts'],b['facts']))
  if lost_critical or (a['complete'] and not b['complete']) or sum(b['facts'])<sum(a['facts']) or (b['critical_issue'] and not a['critical_issue']) or (b['unsupported_claim'] and not a['unsupported_claim']) or (a['citations_supported'] and not b['citations_supported']):regressions.append({'case':r['case'],'repeat':r['repeat'],'A':a,'B':b})
 summary={'status':run.load('run-status.json'),'physical':physical,'allocated_groups':groups,'heldout_regressions':regressions,
 'money_gate':'undetermined: no per-call subscription billing','quality_gate':('fail' if regressions else 'no_observed_regression') if len(grades)==len(rows)==48 else 'incomplete',
 'acceptance':'not established','grades_count':len(grades),'source_drift':[]}
 for ps in run.load('corpus.json').values():
  for p in ps:
   if run.sha(run.ROOT/p['path'])!=p['source_sha256'] and p['path'] not in summary['source_drift']:summary['source_drift'].append(p['path'])
 run.save('summary.json',summary)
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
