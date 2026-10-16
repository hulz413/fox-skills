"""Post-run accounting only. No service calls or policy changes."""
import json,random,statistics
import run as r
H=r.HERE

def rows(n):return [json.loads(x) for x in (H/n).read_text().splitlines()] if (H/n).exists() else []
def mask():
 ps={p['id']:p for p in r.t.load('samples.json')};items=[];mapping={}
 for result in rows('results.jsonl'):
  p=ps[result['packet']]
  for task in p['tasks']:
   items.append((result,task))
 random.Random(946182).shuffle(items);masked=[]
 for i,(result,task) in enumerate(items,1):
  rid=f'R{i:02}';mapping[rid]={'packet':result['packet'],'task':task['id'],'arm':result['arm']}
  masked.append({'review_id':rid,'task':r.taskpublic(task),'gold':task['gold'],'initial':result['initial'][task['id']],'final':result['final'][task['id']],'initial_evidence':result['selected'][task['id']],'repaired':task['id'] in result['repairs']})
 r.t.save('masked-review.json',masked);r.t.save('review-mapping.json',mapping)
 print('Masked completed task answers:',len(masked))

def analyze():
 r.verify();ps={p['id']:p for p in r.t.load('samples.json')};cs=rows('calls.jsonl');rs=rows('results.jsonl')
 scores=r.t.load('review-scores.json') if (H/'review-scores.json').exists() else []
 mapping=r.t.load('review-mapping.json') if (H/'review-mapping.json').exists() else {}
 grades={(mapping[g['review_id']]['packet'],mapping[g['review_id']]['arm'],mapping[g['review_id']]['task']):g for g in scores}
 def usage(c):return c.get('usage') if c['backend']=='codex_cli' else (c.get('response') or {}).get('usage')
 def account(calls):
  out={}
  for b in ('codex_cli','typesafe'):
   sub=[c for c in calls if c['backend']==b];us=[usage(c) for c in sub];known=[u for u in us if u]
   out[b]={'calls':len(sub),'usage_missing_calls':sum(not u for u in us),'input_tokens':sum(u.get('input_tokens',0) for u in known),'output_tokens':sum(u.get('output_tokens',0) for u in known),'cached_input_tokens_reported':sum(u.get('cached_input_tokens',0) for u in known),'seconds_sum':sum(c['seconds'] for c in sub)}
  out['known_total_tokens']=sum(out[b]['input_tokens']+out[b]['output_tokens'] for b in ('codex_cli','typesafe'))
  return out
 groups={};missing=[]
 for split in ('calibration','holdout'):
  groups[split]={}
  for arm in ('A','B'):
   rr=[x for x in rs if x['split']==split and x['arm']==arm];ids={x['packet'] for x in rr}
   calls=[c for c in cs if c['split']==split and c['arm']==arm and c.get('packet',c['case']) in ids]
   gd=[g for (pid,a,task),g in grades.items() if pid in ids and a==arm]
   for result in rr:
    for task in ps[result['packet']]['tasks']:
     have=set(result['selected'][task['id']]);lost=[i for i,f in enumerate(task['gold']) if not any(set(ss)<=have for ss in f['sufficient_sets'])]
     if lost:missing.append({'packet':result['packet'],'arm':arm,'task':task['id'],'facts':lost,'critical':[i for i in lost if task['gold'][i]['critical']]})
   rework=[c for c in calls if c['phase'] in ('repair','recheck')]
   groups[split][arm]={'completed_packet_arms':len(rr),'completed_tasks':3*len(rr),'operational_accepted_packets':sum(x['accepted'] for x in rr),'accounting':account(calls),'seconds':sum(x['seconds'] for x in rr),'mean_seconds':statistics.mean(x['seconds'] for x in rr) if rr else None,'repair_tasks':sum(len(x['repairs']) for x in rr),'worker_requested_tasks':sum(bool(a['requested_ids'] or a['missing']) for x in rr for a in x['initial'].values()),'rework_accounting':account(rework),'graded_tasks':len(gd),'initial_fact_coverage':statistics.mean(sum(g['initial_facts'])/len(g['initial_facts']) for g in gd) if gd else None,'final_fact_coverage':statistics.mean(sum(g['final_facts'])/len(g['final_facts']) for g in gd) if gd else None,'final_complete_supported':sum(all(g['final_facts']) and not g['final_critical_error'] and not g['final_unsupported'] and g['final_citations_supported'] for g in gd)}
 held=[x for x in rs if x['split']=='holdout'];complete=len(rs)==12 and len(held)==8 and len(scores)==36
 ga=groups['holdout']['A'];gb=groups['holdout']['B'];delta=None
 if ga['completed_packet_arms']==gb['completed_packet_arms']==4:
  delta={'total_token_reduction':1-gb['accounting']['known_total_tokens']/ga['accounting']['known_total_tokens'],'wall_time_reduction':1-gb['seconds']/ga['seconds']}
 regressions=[]
 for (pid,arm,tid),b in grades.items():
  if arm!='B' or ps[pid]['split']!='holdout':continue
  a=grades.get((pid,'A',tid))
  if a and (sum(b['final_facts'])<sum(a['final_facts']) or (b['final_critical_error'] and not a['final_critical_error']) or (b['final_unsupported'] and not a['final_unsupported']) or (a['final_citations_supported'] and not b['final_citations_supported'])):regressions.append(tid)
 verdict='incomplete'
 if complete:
  quality=gb['final_complete_supported']==12 and not regressions and all(x['accepted'] for x in held)
  verdict='pass' if quality and delta['total_token_reduction']>=.15 and delta['wall_time_reduction']>=.10 else 'fail'
 result={'status':r.t.load('run-status.json'),'physical_all_calls':account(cs),'groups_completed_only':groups,'heldout_reductions':delta,'allocation_missing_minimum_evidence':missing,'heldout_final_quality_regressions':regressions,'acceptance':verdict,'sources_drifted':sorted({f['path'] for p in ps.values() for f in p['fragments'] if r.t.sha(r.ROOT/f['path'])!=f['source_sha256']})}
 r.t.save('summary.json',result);print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':
 import sys
 mask() if '--mask' in sys.argv else analyze()
