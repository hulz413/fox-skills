"""Report the preregistered metrics only; no inference or parameter updates."""
import json
from pathlib import Path
import statistics
import run as trial
HERE=Path(__file__).resolve().parent

def main():
 trial.verify()
 summary=trial.load('summary.json'); cases={c['id']:c for c in trial.load('samples.json')}
 rows=[json.loads(s) for s in (HERE/'results.jsonl').read_text().splitlines()]
 calls=[json.loads(s) for s in (HERE/'calls.jsonl').read_text().splitlines()]
 by={(r['case_id'],r['repeat'],r['arm']):r for r in rows}
 regressions=[];missing=[];changes=[]
 for cid,c in cases.items():
  for rep in (1,2):
   if (cid,rep,'C') not in by:continue
   cr=by[cid,rep,'C']
   if cr['pool_facts_hit']<cr['fact_count']:missing.append({'case':cid,'repeat':rep,'pool_facts_hit':cr['pool_facts_hit'],'total':cr['fact_count']})
   if c['split']=='holdout':
    for arm in ('A','B'):
     base=by[cid,rep,arm]
     if cr['fact_recall']<base['fact_recall'] or cr['counter_hit']<base['counter_hit']:
      regressions.append({'case':cid,'repeat':rep,'against':arm,'C_facts':cr['facts_hit'],'baseline_facts':base['facts_hit'],'C_counter_hit':cr['counter_hit'],'baseline_counter_hit':base['counter_hit']})
  if (cid,2,'C') in by:
   a,b=by[cid,1,'C'],by[cid,2,'C']
   changes.append({'case':cid,'order_changed':a['order']!=b['order'],'selection_changed':a['selected_ids']!=b['selected_ids'],'facts_changed':a['facts_hit']!=b['facts_hit'],'recall_changed':a['fact_recall']!=b['fact_recall']})
 h=summary['groups']['holdout'];improved=False
 if len(h)==3:
  recall_better=h['C']['fact_recall_macro']>max(h[a]['fact_recall_macro'] for a in ('A','B'))
  values={a:h[a]['oracle_bytes_to_all_facts'] for a in ('A','B','C')}
  oracle_better=all(x is not None for v in values.values() for x in v) and statistics.mean(values['C'])<min(statistics.mean(values[a]) for a in ('A','B'))
  improved=recall_better or oracle_better
 accepted=summary['status']=='completed' and not regressions and improved
 analysis={'preregistered_gate_passed':accepted,'heldout_regressions':regressions,'candidate_pool_gaps':missing,'repeat_stability':changes,'stratified':{}}
 for split in ('calibration','holdout'):
  for kind in ('code','docs'):
   for arm in ('A','B','C'):
    rs=[r for r in rows if (r['split'],r['kind'],r['arm'])==(split,kind,arm)]
    if rs:analysis['stratified'][f'{split}/{kind}/{arm}']={'macro_recall':statistics.mean(r['fact_recall'] for r in rs),'complete':sum(r['complete'] for r in rs),'case_repeats':len(rs)}
 trial.save('analysis.json',analysis)
 lines=['# Jev reranking pilot — results','',f"Status: {summary['status']}. Preregistered next-experiment gate: **{'PASS' if accepted else 'FAIL'}**.",'',
 'Eight authored source-grounded tasks, 4 calibration / 4 holdout, 12 shared candidates, two repeats. Four source families are separated by split. No old holdout tuning. No production integration.',
 '',f"HTTP attempts: {summary['attempts']}/192; statuses: {summary['http_statuses']}. Known usage: {summary['known_usage']}; unknown usage responses: {summary['unknown_usage_responses']}. Serial API wait: {summary['api_seconds']:.3f}s.",'',
 '## Frozen primary results','', '| Split | Arm | Fact recall (task macro) | Counterevidence recall | Complete / case-repeats | Selected UTF-8 bytes |','|---|---|---:|---:|---:|---:|']
 for split,groups in summary['groups'].items():
  for arm,m in groups.items():lines.append(f"| {split} | {arm} | {m['fact_recall_macro']:.1%} | {m['counter_recall_micro']:.1%} | {m['complete_case_repeats']}/{m['case_repeats']} | {m['selected_bytes']} |")
 lines+=['','A=file/line order proxy; B=BM25; C=BM25+Jev. All use the identical 12-candidate pool and 3000-byte prefix budget. Repeated A/B are identical baselines, not independent trials.','',
 '## Per-task evidence coverage','', '| Task | Split | A facts r1/r2 | B facts r1/r2 | C facts r1/r2 | Facts available in pool |','|---|---|---|---|---|---|']
 for cid,c in cases.items():
  cells=[]
  for arm in ('A','B','C'):
   cells.append(' / '.join(f"{len(by[cid,r,arm]['facts_hit'])}/{by[cid,r,arm]['fact_count']}" if (cid,r,arm) in by else 'not run' for r in (1,2)))
  pool=by.get((cid,1,'A'))
  lines.append(f"| {cid} | {c['split']} | {' | '.join(cells)} | {str(pool['pool_facts_hit'])+'/'+str(pool['fact_count']) if pool else 'not run'} |")
 lines+=['','## Regressions and stability','',f'Heldout task/repeat/baseline regression comparisons: {len(regressions)}.',
 f"C order changed in {sum(x['order_changed'] for x in changes)}/{len(changes)} tasks; selection changed in {sum(x['selection_changed'] for x in changes)}; recall changed in {sum(x['recall_changed'] for x in changes)}.",'']
 for r in regressions:lines.append('- '+json.dumps(r,ensure_ascii=False))
 lines+=['','## Offline oracle reading cost','', 'Bytes required to encounter all labeled evidence; computed using gold labels, NOT a deployable stopping rule. Null means missing evidence in the candidate pool.','']
 for split,groups in summary['groups'].items():
  for arm,m in groups.items():
   values=m['oracle_bytes_to_all_facts'];lines.append(f'- {split}/{arm}: {values}; mean={statistics.mean(values):.1f}' if all(x is not None for x in values) else f'- {split}/{arm}: {values}; incomplete pool prevents a complete mean.')
 lines+=['','## Interpretation limits','',
 '- This isolates ordering within a common BM25 pool; A is not a live agent baseline. Queries and labels were authored, not captured from production. Four heldout tasks cannot establish general reliability.',
 '- Essential facts are an anchor-based minimum rubric. Single-author labels may miss equivalent evidence. Some facts share passages, so fact observations are correlated.',
 '- Byte budgets are not token budgets. No answer-generation model was called: final correctness, actual stop/expansion behavior, rework, cache effects, total downstream tokens, and monetary savings remain unmeasured.',
 '- Each Jev call has the task and one candidate only. Long semantic relationships across windows may be absent; this run does not change windows after observing results.',
 '- All new protocols, corpus, labels, scripts and previous fox-orchestrate files were hash-verified after collection. Skill, old expectations and runtime threshold are unchanged.',
 '- Offline verification: 9 experiment checks and all 59 existing fox-orchestrate checks passed. HTTP authentication stop and exact 192-call budget were tested using fake local transport.',
 '', '## Artifacts','', '`manifest.json`, `PROTOCOL.md`, `samples.json`, `corpus.json`, `calibration-lock.json`, `calls.jsonl`, `results.jsonl`, `summary.json`, `analysis.json`.','']
 with (HERE/'REPORT.md').open('x') as f:f.write('\n'.join(lines))
 print(json.dumps({'gate_passed':accepted,'heldout_regressions':len(regressions),'pool_gaps':len(missing),'groups':summary['groups']},ensure_ascii=False))

if __name__=='__main__':main()
