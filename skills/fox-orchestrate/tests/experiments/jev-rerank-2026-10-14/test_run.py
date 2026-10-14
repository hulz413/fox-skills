import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import run as trial

class EvaluationChecks(unittest.TestCase):
 def test_split_disjoint(self):
  s=trial.load('samples.json')
  self.assertFalse({c['family'] for c in s if c['split']=='calibration'} & {c['family'] for c in s if c['split']=='holdout'})
 def test_anchor_provenance(self):
  corpus=trial.load('corpus.json')
  for ps in corpus.values():
   for p in ps:
    lines=(trial.ROOT/p['path']).read_text().splitlines(keepends=True)
    self.assertTrue(''.join(lines[p['line']-1:]).startswith(p['text']))
    self.assertEqual(trial.sha(trial.ROOT/p['path']),p['sha256'])
 def test_joint_evidence_required(self):
  f={'evidence_alternatives':[['a','b'],['c']]}
  self.assertFalse(trial.covered(f,['a']));self.assertTrue(trial.covered(f,['a','b']));self.assertTrue(trial.covered(f,['c']))
 def test_budget_does_not_skip(self):
  p=lambda i,text:dict(id=i,path='p',line=1,text=text)
  case={'facts':[{'id':'f','evidence_alternatives':[['b']],'counterevidence':True}]}
  r=trial.metrics(case,[p('a','x'*trial.BUDGET),p('b','tiny')])
  self.assertEqual(r['selected_ids'],[]);self.assertEqual(r['fact_recall'],0)
 def test_request_has_no_labels(self):
  corpus=trial.load('corpus.json')
  for c in trial.load('samples.json'):
   r=trial.request(c,corpus[c['family']][0]);self.assertEqual(set(r['state']),{'task','candidate'})
   self.assertEqual(set(r['state']['candidate']),{'path','line','text'})
 def test_invalid_response(self):
  for v in (True,float('nan'),1.1,-.1,'0.5'):
   with self.assertRaises(ValueError):trial.probability(self.row(v))
 @staticmethod
 def row(v=.8,status=200):
  return {'http_status':status,'response':{'model':trial.MODEL,'answers':{'useful':{'type':'noul','noul':v}},'usage':{'input_tokens':1,'output_tokens':1}},'latency_seconds':.001,'error':None}
 def exercise(self,fail_at=None,status=401):
  original=trial.HERE;cases=trial.load('samples.json');corpus=trial.load('corpus.json')
  pools={c['id']:[p['id'] for p in trial.bm25(c,corpus[c['family']])[:trial.POOL]] for c in cases}
  count=0
  def transport(payload):
   nonlocal count
   count+=1;return self.row(status=status if count==fail_at else 200)
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)
   for n in ('samples.json','corpus.json'):(root/n).write_bytes((original/n).read_bytes())
   (root/'manifest.json').write_text('{}')
   with patch.object(trial,'HERE',root),patch.object(trial,'verify',return_value={'pools':pools}),patch.object(trial,'transport',side_effect=transport),patch.dict('os.environ',{'TYPESAFE_API_KEY':'fake-local-only'}),contextlib.redirect_stdout(io.StringIO()):trial.run()
   summary=json.loads((root/'summary.json').read_text())
   self.assertEqual(summary['attempts'],count)
   self.assertEqual((root/'calibration-lock.json').exists(),count>96)
   return count,summary['status']
 def test_auth_stop_calibration(self):self.assertEqual(self.exercise(1),(1,'stopped_auth_failure'))
 def test_auth_stop_holdout(self):self.assertEqual(self.exercise(97,403),(97,'stopped_auth_failure'))
 def test_exact_budget(self):self.assertEqual(self.exercise(),(192,'completed'))

if __name__=='__main__':unittest.main()
