"""Build source-grounded audit tasks. No inference. No previous experimental labels."""
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
FILES={
 'orca':['skills/orca-cli/SKILL.md'],
 'anatomy':['skills/anatomy/scripts/chrome-port.mjs','skills/anatomy/scripts/publish.mjs'],
 'commit':['skills/fox-commit/SKILL.md'],
 'archify_docs':['skills/archify/references/delivery-contract.md'],
 'archify_code':['skills/archify/renderers/shared/sidecar-path.mjs','skills/archify/renderers/shared/owned-temp-directory.mjs','skills/archify/renderers/shared/portable-path.mjs'],
}
def save(n,v):
 with (HERE/n).open('x') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
corpus={}
for family,paths in FILES.items():
 units=[]
 for path in sorted(paths):
  src=(ROOT/path).read_text();lines=src.splitlines(keepends=True)
  if path.endswith('.mjs'):
   starts=[i for i,l in enumerate(lines) if re.match(r'^(?:export )?(?:async )?function ',l)]
   header=''.join(lines[:starts[0]]) if starts else ''
  else:
   starts=[];fence=False
   for i,l in enumerate(lines):
    if l.lstrip().startswith('```'):fence=not fence
    if not fence and l.startswith('## '):starts.append(i)
   header=''.join(lines[:starts[0]]) if starts else ''
  if not starts:starts=[0]
  for a,b in zip(starts,starts[1:]+[len(lines)]):
   text=''.join(lines[a:b]);assert text.strip()
   units.append({'id':f'{family}-{len(units)+1:02}','path':path,'line':a+1,'header':header,'text':text,'source_sha256':hashlib.sha256(src.encode()).hexdigest()})
 corpus[family]=units
cases=[]
def add(cid,split,family,kind,q,facts):
 labels=[]
 for claim,needle,critical in facts:
  units=[p['id'] for p in corpus[family] if needle in p['text'] or needle in p['header']]
  assert units,(cid,needle)
  labels.append({'claim':claim,'anchor':needle,'sources':units,'critical':critical})
 cases.append({'id':cid,'split':split,'family':family,'kind':kind,'task':q,'rubric':labels})
add('N01','calibration','orca','docs','How is the Orca executable selected across explicit overrides, a development checkout, and Linux outside Orca? May a failed executable be replaced silently?',[
 ('ORCA_CLI_COMMAND takes precedence','If the `ORCA_CLI_COMMAND` environment variable is set',True),
 ('then dev checkout exposes ORCA_DEV_REPO_ROOT -> orca-dev','ORCA_DEV_REPO_ROOT',False),
 ('Linux outside Orca uses orca-ide; bare orca may be screen reader','GNOME Orca screen reader',True),
 ('selected executable failure is reported and stops; no fallback','Do not fall through',True)])
add('N02','calibration','orca','docs','Orca 文档加载命令和推荐输出格式是什么？区分 not running、runtime_access_denied 和 skills get 未知时的处理，先不要实际执行。',[
 ('load guide via selected CLI skills get orca-cli','ORCA skills get orca-cli',False),
 ('prefer JSON','Prefer `--json`',False),
 ('not running: selected CLI open --json and retry','start it with `ORCA open --json`',False),
 ('runtime access denied: escalate, not restart','do not run `ORCA open` or restart Orca',True),
 ('unknown skills get: explain update, read-only help, no guessing','do not guess unsupported commands',True)])
add('N03','calibration','anatomy','code','chromePort 如何识别启动成功并返回端口？如果超时或进程提前退出，如何清理监听器、Chrome 和临时 profile？',[
 ('parse DevTools listening websocket port from stderr','DevTools listening on ws:',False),
 ('timeout is 20000 ms','20000',False),
 ('clean removes timer and data/error/exit listeners','chrome.stderr.off("data", data)',False),
 ('failure kills SIGKILL, deletes profile recursively, rethrows','chrome.kill("SIGKILL")',True)])
add('N04','calibration','anatomy','code','In rewriteSkillPaths, how are references within the figure source, within the skill, and outside both treated? Does reporting outside references rewrite or fetch them?',[
 ('inside source: absolute paths become relative, existing relative paths retained','if (inside(source, target))',False),
 ('skill references redirected through skillLink relative to destination','if (inside(skill, target))',False),
 ('outside code/assets extensions are collected but original literal returned','outside.push(path)',True),
 ('function returns rewritten text and outside list, no fetch','return { text: rewritten, outside }',True)])
add('N05','holdout','commit','docs','What activates fox-commit, how many commits does it authorize, and which files should be staged if nothing is staged but unrelated edits exist?',[
 ('only explicit fox-commit activation; generic commit does not activate','Do not invoke it automatically for a generic request',True),
 ('exactly one commit','Create exactly one commit.',True),
 ('review then stage only relevant reviewed files; not add -A by default','Do not use `git add -A` by default.',True),
 ('ask if unrelated/surprising changes or cannot safely determine files','intended files cannot be determined safely',True)])
add('N06','holdout','commit','docs','fox-commit 应使用什么模型和 effort？没有运行时 effort 控制能不能继续，是否可以修改全局默认值？提交后需要报告什么？',[
 ('current session current model','directly in the current session using its current model',True),
 ('lowest supported effort when control exists, respect overrides','respecting explicit user overrides',False),
 ('no control: continue actual setting and disclose, not claim lower effort','continue at the actual setting',True),
 ('do not change model or global defaults','do not change the model or global defaults',True),
 ('report hash and final subject','report the commit hash and final subject',False)])
add('N07','holdout','archify_docs','docs','Archify 的 delivery 锁是按 artifact 还是目录生效？已确认 PID 死亡的锁会自动清除吗，人工恢复应保留哪些文件？',[
 ('physical output directory mutex serializes different artifact names too','different artifact names in one directory also run serially',False),
 ('known-dead PID: exit 1 delivery/lock-stale and preserve files','delivery/lock-stale',True),
 ('stop attempts, verify no owner/no replaced entry, remove only reported lock','remove only the reported lock',True),
 ('preserve artifact provenance pending journal during stale lock recovery','Do not\nremove an artifact, current provenance, or pending journal',True)])
add('N08','holdout','archify_docs','docs','After editing a candidate with browser evidence, should I change the HTML path or the evidence directory? Can failed automatic opening invalidate a verified delivery?',[
 ('fresh evidence dir for changed bytes, retain requested HTML path','Keep the requested HTML path stable.',True),
 ('reuse evidence dir for retries of unchanged bytes','retain the same directory for retries of unchanged bytes',False),
 ('never remove unknown evidence to pass','Never remove unknown evidence',True),
 ('optional opening failure does not invalidate delivery','Failure or unsupported opening does not invalidate delivery',True)])
add('N09','holdout','archify_code','code','When does boundedSidecarStem keep the original stem, and how does it bound long names without cutting Unicode code points? What size limits are checked?',[
 ('keep only if not forced, fits suffixes, and not reserved hash namespace','if (!force && !sidecarStemNeedsBounding',False),
 ('check both JS string length and UTF8 byte length <=255 for each suffix','Buffer.byteLength(value, \'utf8\') <= 255',True),
 ('sha256 marker with optional hashDomain plus NUL','const hashInput = hashDomain',False),
 ('spread into code points then pop until fits','const codePoints = [...stem]',True)])
add('N10','holdout','archify_code','code','How does sidecarStemFromComponent treat .html compared with other extensions? Is its extension comparison case-sensitive, and how can an already bounded stem be identified?',[
 ('exact lowercase .html suffix strips extension, options undefined','component.endsWith(\'.html\')',False),
 ('other component retained, force true and full-component domain','hashDomain: \'full-component\'',True),
 ('endsWith is case sensitive so .HTML takes other branch','component.endsWith(\'.html\')',False),
 ('bounded marker regex case insensitive ending hash64','SIDECAR_STEM_NAMESPACE.test(stem)',False)])
add('N11','holdout','archify_code','code','createOwnedTempDirectory 的 cleanup 如何避免删掉被替换的路径？哪些错误重试、最多几次？这些检查是否保证消除了恶意竞态？',[
 ('verify ancestors and directory dev/inode/birthtime every attempt','verifyIdentity(identity)',True),
 ('retry EBUSY EPERM EACCES ENOTEMPTY, 3 retries after initial','attempt < 3',False),
 ('rm internal retries disabled, force false','force: false, maxRetries: 0',True),
 ('path check/rm race remains, not filesystem sandbox','this is not a filesystem sandbox',True),
 ('failure retains path and ARCHIFY_TEMP_CLEANUP','ARCHIFY_TEMP_CLEANUP',False)])
add('N12','holdout','archify_code','code','Compare portable path profiles repo, output, archive. Which universal path rejections apply, and which Windows filename checks and component length limits are additional?',[
 ('valid profiles repo output archive','PORTABLE_PATH_PROFILES',False),
 ('all reject absolute/drive-relative/URI/backslash/empty/dot/control/unpaired surrogate','Portable path must not contain dot segments.',True),
 ('Windows constraints only output/archive; repo skips those','if (!WINDOWS_SAFE_PROFILES.has(profile)) continue;',True),
 ('Windows extra ADS invalid chars trailing dot/space reserved/short names','Portable path must not use a reserved Windows device name.',True),
 ('Windows safe component <=255 both UTF8 bytes UTF16 code units','utf8Bytes > 255 || utf16CodeUnits > 255',True)])
save('corpus.json',corpus);save('samples.json',cases)
print('Authored current-repository audit tasks:',len(cases),'not historical user tasks; corpus units:',{k:len(v) for k,v in corpus.items()})
