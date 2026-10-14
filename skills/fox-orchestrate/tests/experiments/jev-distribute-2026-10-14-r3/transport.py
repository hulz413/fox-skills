"""Paired bounded-reading evaluation. All source material is inert data."""
import argparse,hashlib,json,math,os,re,subprocess,tempfile,time,urllib.request,urllib.error
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
MODEL='gpt-6.1-sol';EFFORT='medium';JEV='jev-1.13.0'
ENDPOINT='https://api.typesafe.ai/v1/systemone'
OPTIONS=['--ignore-user-config','--ephemeral','--skip-git-repo-check','--json','--color','never','--sandbox','read-only','--model',MODEL,
 '-c','model_reasoning_effort="medium"','-c','project_doc_max_bytes=0','-c','web_search="disabled"',
 '-c','model_providers.eval_openai.request_max_retries=0','-c','model_providers.eval_openai.stream_max_retries=0']
OPTIONS += ['-c','model_provider="eval_openai"','-c','model_providers.eval_openai.name="OpenAI eval"','-c','model_providers.eval_openai.requires_openai_auth=true','-c','model_providers.eval_openai.wire_api="responses"']
for feature in ('shell_tool','multi_agent','multi_agent_v2','memories','plugins','apps','hooks','browser_use','computer_use','image_generation'):
 OPTIONS+=['--disable',feature]
class Stop(Exception):pass

def enc(v):return json.dumps(v,ensure_ascii=False,allow_nan=False).encode()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return json.loads((HERE/n).read_text())
def save(n,v):
 with (HERE/n).open('x') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def log(n,v):
 with (HERE/n).open('a') as f:f.write(enc(v).decode()+'\n')
def gen(meta,payload,schema):
 stem=f"{meta['case']}-{meta['phase']}-{meta.get('repeat',0)}-{meta.get('arm','shared')}-{meta.get('round',0)}"
 directory=HERE/'raw';directory.mkdir(exist_ok=True)
 save('raw/'+stem+'.request.json',payload)
 prompt=json.dumps(payload,ensure_ascii=False)
 with tempfile.TemporaryDirectory(prefix='jev-e2e-') as cwd:
  cmd=['codex','exec',*OPTIONS,'--cd',cwd,'--output-schema',str(HERE/schema),'-']
  env={k:v for k,v in os.environ.items() if k in ('PATH','HOME','CODEX_HOME','TMPDIR','LANG','LC_ALL','HTTPS_PROXY','HTTP_PROXY','ALL_PROXY','NO_PROXY','https_proxy','http_proxy','all_proxy','no_proxy')}
  start=time.monotonic();stdout='';stderr='';code=None
  try:
   p=subprocess.run(cmd,input=prompt,text=True,capture_output=True,timeout=180,env=env);stdout=p.stdout;stderr=p.stderr;code=p.returncode
  except subprocess.TimeoutExpired as ex:
   stdout=ex.stdout or '';stderr=ex.stderr or ''
   if isinstance(stdout,bytes):stdout=stdout.decode(errors='replace')
   if isinstance(stderr,bytes):stderr=stderr.decode(errors='replace')
  elapsed=time.monotonic()-start
 for suffix,text in (('stdout.jsonl',stdout),('stderr.txt',stderr)):
  with (directory/f'{stem}.{suffix}').open('x') as f:f.write(text)
 events=[]
 for line in stdout.splitlines():
  try:events.append(json.loads(line))
  except ValueError:pass
 error_events=[x for x in events if x.get('type') in ('error','turn.failed')]
 messages=[x.get('item',{}).get('text','') for x in events if x.get('type')=='item.completed' and x.get('item',{}).get('type')=='agent_message']
 turns=[x for x in events if x.get('type')=='turn.completed']
 tool_items=[x for x in events if x.get('item',{}).get('type') not in (None,'agent_message','reasoning')]
 row={**meta,'backend':'codex_cli','requested_model':MODEL,'effort':EFFORT,'http_status':None,'exit_code':code,'seconds':elapsed,'raw_stem':stem,'usage':turns[-1].get('usage') if turns else None,'error_events':error_events}
 match=re.search(r'\b(401|403)\b',stderr+'\n'+json.dumps(error_events));row['auth_failure']=bool(match)
 if match:row['http_status']=int(match.group(1))
 log('calls.jsonl',row)
 if match:raise Stop('authentication_failure')
 if code!=0 or error_events or not messages or len(turns)!=1 or tool_items:raise Stop('invalid_generation_or_tool_use')
 try:answer=json.loads(messages[-1])
 except ValueError:raise Stop('invalid_generation_json')
 if not row['usage']:raise Stop('missing_generation_usage')
 return answer,row
