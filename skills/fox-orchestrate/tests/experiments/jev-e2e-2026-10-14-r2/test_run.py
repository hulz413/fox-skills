import unittest,json,math,tempfile,contextlib,io
from pathlib import Path
from unittest.mock import patch
import run as r
class Checks(unittest.TestCase):
 def test_split(self):
  cs=r.load('samples.json');self.assertEqual(len(cs),12)
  self.assertFalse({c['family'].split('_')[0] for c in cs if c['split']=='calibration'} & {c['family'].split('_')[0] for c in cs if c['split']=='holdout'})
 def test_roundrobin(self):
  p=lambda s:dict(id=s)
  ls=[[p('a'),p('b'),p('c')],[p('a'),p('d'),p('b')]]
  self.assertEqual([x['id'] for x in r.interleave(ls)],['a','d','b','c'])
 def test_complete_units(self):
  for units in r.load('corpus.json').values():
   for p in units:
    lines=(r.ROOT/p['path']).read_text().splitlines(keepends=True)
    self.assertTrue(''.join(lines[p['line']-1:]).startswith(p['text']))
    self.assertEqual(r.sha(r.ROOT/p['path']),p['source_sha256'])
    if p['path'].endswith('.mjs'):self.assertRegex(p['text'],r'^(export )?(async )?function ')
 def test_no_labels_in_public(self):
  for units in r.load('corpus.json').values():
   for p in units:self.assertEqual(set(r.public(p)),{'id','path','line','header','text'})
 def test_budget_and_immediate_stop(self):
  original=r.HERE
  for fail in (True,False):
   counts={'query':0,'answer':0,'jev':0}
   def gen(meta,payload,schema):
    counts[meta['phase']]+=1
    if fail:raise r.Stop('authentication_failure')
    if meta['phase']=='query':return {'subquestions':[{'question':'task','query':'task'}]}, {'seconds':.1,'usage':{'input_tokens':1,'output_tokens':1}}
    return {'decision':'read_more','answer':'insufficient','citations':[],'missing':['x']},{'seconds':.1,'usage':{'input_tokens':1,'output_tokens':1}}
   def jev(*args):counts['jev']+=1;return [.5],{'seconds':.1}
   with tempfile.TemporaryDirectory() as td:
    p=Path(td)
    for n in ('samples.json','corpus.json'):(p/n).write_bytes((original/n).read_bytes())
    (p/'manifest.json').write_text('{}')
    def logged(n,v):
     with (p/n).open('a') as f:f.write(json.dumps(v)+'\n')
     # Fake transport emits one placeholder call log; no service is contacted.
     if not (p/'calls.jsonl').exists():(p/'calls.jsonl').write_text('{}\n')
    # Starting marker is created after the real runner's no-existing-run check.
    real_save=r.save
    def save(n,v):
     if n.endswith('-queries.json') and not (p/'calls.jsonl').exists():(p/'calls.jsonl').write_text('{}\n')
     real_save(n,v)
    with patch.object(r,'HERE',p),patch.object(r,'verify',return_value={}),patch.object(r,'gen',side_effect=gen),patch.object(r,'jev',side_effect=jev),patch.object(r,'save',side_effect=save),patch.dict('os.environ',{'TYPESAFE_API_KEY':'fake'}),contextlib.redirect_stdout(io.StringIO()):
     (p/'calls.jsonl').unlink(missing_ok=True);r.run()
    state=json.loads((p/'run-status.json').read_text())
    if fail:self.assertEqual(counts,{'query':1,'answer':0,'jev':0});self.assertEqual(state['status'],'authentication_failure')
    else:self.assertEqual(counts['query'],12);self.assertLessEqual(counts['answer'],144);self.assertLessEqual(counts['jev'],288);self.assertEqual(state['completed_arm_runs'],48)
if __name__=='__main__':unittest.main()
