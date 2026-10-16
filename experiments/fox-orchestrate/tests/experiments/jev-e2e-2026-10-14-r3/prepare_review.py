"""Mask final answer group identities; do not score by anchor occurrence."""
import json,random
from pathlib import Path
HERE=Path(__file__).resolve().parent
cases={c['id']:c for c in json.loads((HERE/'samples.json').read_text())}
rows=[json.loads(x) for x in (HERE/'results.jsonl').read_text().splitlines()]
random.Random(724913).shuffle(rows)
review=[];mapping={}
for i,r in enumerate(rows,1):
 rid=f'R{i:02}'
 mapping[rid]={k:r[k] for k in ('case','split','repeat','arm')}
 review.append({'review_id':rid,'task':cases[r['case']]['task'],'rubric':cases[r['case']]['rubric'],'final':r['final'],'read_passage_ids':r['selected']})
for name,value in [('masked-review.json',review),('review-mapping.json',mapping)]:
 with (HERE/name).open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
print('Masked records:',len(review),'Group mapping saved separately; reviewer is not independent.')
