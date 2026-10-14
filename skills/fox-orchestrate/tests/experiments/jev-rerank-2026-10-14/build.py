"""Build new source-grounded retrieval tasks; no service calls or outcome-based selection."""
import ast
import hashlib
import json
import re
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]

def dump(name, value):
    with (HERE/name).open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2); f.write('\n')

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

families = {
 'advisor': ['skills/fox-ask-advisor/SKILL.md'],
 'installer': ['skills/.system/skill-installer/scripts/install-skill-from-github.py','skills/.system/skill-installer/scripts/list-skills.py','skills/.system/skill-installer/scripts/github_utils.py'],
 'creator': ['skills/.system/skill-creator/scripts/init_skill.py','skills/.system/skill-creator/scripts/quick_validate.py','skills/.system/skill-creator/scripts/generate_openai_yaml.py'],
 'browser': ['skills/playwright-cli/SKILL.md','skills/playwright-cli/references/session-management.md','skills/playwright-cli/references/storage-state.md'],
}
corpus={}
for family, paths in families.items():
    pieces=[]
    for path in sorted(paths):
        text=(ROOT/path).read_text(); lines=text.splitlines(keepends=True)
        # Semantic boundaries: Python top-level definitions; Markdown headings and blank paragraphs.
        if path.endswith('.py'):
            tree=ast.parse(text)
            starts=sorted({0,len(lines)} | {n.lineno-1 for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))})
        else:
            starts=sorted({0,len(lines)} | {i for i,l in enumerate(lines) if l.startswith('#') or (i and not lines[i-1].strip())})
        # Pack adjacent units up to 1200 UTF-8 bytes; split large units only on whole lines.
        chunks=[]; buf=''; begin=0
        for a,b in zip(starts,starts[1:]):
            unit=''.join(lines[a:b])
            if buf and len((buf+unit).encode())>1200:
                chunks.append((begin,buf));buf=''
            if not buf: begin=a
            if len(unit.encode())<=1200:
                buf+=unit
            else:
                for i in range(a,b):
                    if buf and len((buf+lines[i]).encode())>1200:
                        chunks.append((begin,buf));buf='';begin=i
                    buf+=lines[i]
        if buf: chunks.append((begin,buf))
        for start,chunk in chunks:
            if not chunk.strip():continue
            pieces.append({'id':f'{family}-{len(pieces)+1:03}', 'path':path,'line':start+1,'text':chunk,'sha256':sha(ROOT/path)})
    corpus[family]=pieces

# Fact labels are source anchors, not inferred from Jev scores. Non-anchor passages are
# unlabeled background, NOT assertions of irrelevance. Counter = refutes tempting premise.
cases=[]
def case(cid,split,family,kind,task,terms,facts):
    annotations=[]
    for fid,claim,needle,counter in facts:
        needles = needle if isinstance(needle,list) else [needle]
        ids=[p['id'] for p in corpus[family] if any(n in p['text'] for n in needles)]
        assert ids,(cid,fid,needle)
        annotations.append({'id':fid,'claim':claim,'anchor':needle,'passage_ids':ids,'evidence_alternatives':[[i] for i in ids],'counterevidence':counter})
    cases.append({'id':cid,'split':split,'family':family,'kind':kind,'task':task,'search_terms':terms.split(),'facts':annotations})
case('D01','calibration','advisor','docs',
 '用户明确要求 full context，同时指定与父会话不同的 model。能否直接 fork，或者自动改 brief？查找约束及无覆盖时的例外。',
 'full context explicit model fork parent brief',[
 ('conflict','显式 full 和显式 model/effort 要求父配置一致，否则解释并询问','An explicit `full` with an explicit model or effort',True),
 ('inherit','显式 full 没有 model/effort 覆盖时接受父配置','An explicit `full` without an explicit model or effort',False),
 ('auto','自动选 full 无法应用配置才改 brief','An automatically selected `full` must not override',True)])
case('D02','calibration','advisor','docs',
 'An explicitly pinned advisor model is unavailable. May we silently use a cheaper model or lower effort? Contrast automatic fallback and shared authentication failures.',
 'fallback explicit model effort authentication provider unavailable',[
 ('pinned','显式 model 不可替换前需询问','An explicitly requested model is pinned.',True),
 ('fixed','自动 fallback 只允许下一候选，provider 和 effort 固定','Keep the selected provider and effort fixed during fallback.',False),
 ('auth','共享认证等失败不能通过换模型规避','Missing provider authentication',True)])
case('C01','calibration','installer','code',
 'Explain installer download-to-git fallback: compare auto HTTP 404, auto HTTP 500 and explicit download mode. What happens if HTTPS git fails?',
 'download auto HTTP git fallback prepare repo',[
 ('download','download 模式下载错误直接抛出','if method == "download":',True),
 ('statuses','auto 仅对 401/403/404 转 git','if "HTTP 401" in err_msg or "HTTP 403" in err_msg or "HTTP 404" in err_msg:',False),
 ('other','其他下载错误抛出','            else:\n                raise',True),
 ('ssh','HTTPS git 失败改 SSH','repo_url = _build_repo_ssh(source.owner, source.repo)',False)])
case('C02','calibration','installer','code',
 '安装器是否允许用 ../ 路径安装或覆盖现有目标？查找路径校验、复制保护及 main 调用这些检查的证据。',
 'path relative destination exists copy validate main',[
 ('relative','拒绝绝对路径和越界相对路径','if os.path.isabs(path) or os.path.normpath(path).startswith(".."):',True),
 ('copy','复制时已存在目标拒绝','if os.path.exists(dest_dir):',True),
 ('caller','main 校验每个 source path','            _validate_relative_path(path)',False),
 ('skill','复制前验证 skill','                _validate_skill(skill_src, repo_root)',False)])
case('D03','holdout','browser','docs',
 '如何隔离两个浏览器会话并保留其中一个的 profile？close 是否等同 delete-data？找命令及默认内存模式的依据。',
 'session persistent profile memory close delete data isolated',[
 ('isolation','-s 隔离浏览器 contexts','Use `-s` flag to isolate browser contexts:',False),
 ('memory','默认 profile 内存，persistent 才持久化',['By default, browser profile is kept in memory only.','Use persistent profile (by default profile is in-memory)'],True),
 ('close','close 停止指定浏览器',['playwright-cli -s=mysession close   # stop a named browser','playwright-cli -s=mysession close  # stop a named browser'],False),
 ('delete','delete-data 删除 profile 数据',['playwright-cli -s=mysession delete-data   # delete named browser data','playwright-cli -s=mysession delete-data  # delete user data for persistent session'],True)])
case('D04','holdout','browser','docs',
 'How can I reuse authenticated browser storage without logging in again, and can I commit the saved auth file? Find save/load commands and credential-file precautions.',
 'storage state save load auth authentication commit tokens',[
 ('save','命名文件保存认证态','playwright-cli state-save',False),
 ('load','加载认证态','playwright-cli state-load',False),
 ('security','认证文件不可提交','Never commit storage state files containing auth tokens',True),
 ('ignore','忽略 auth 文件','Add `*.auth-state.json` to `.gitignore`',False)])
case('C03','holdout','creator','code',
 '初始化 skill 时传入混合大小写和重复资源类型，会如何规范化及去重？已有 skill 目录会被覆盖吗，--examples 无 resources 行不行？',
 'normalize skill name resources examples exists deduped',[
 ('normalize','名称小写','normalized = skill_name.strip().lower()',False),
 ('dedupe','resources 保序去重','        if resource not in seen:',False),
 ('existing','已有目录拒绝','    if skill_dir.exists():',True),
 ('examples','examples 需要 resources','    if args.examples and not resources:',True)])
case('C04','holdout','creator','code',
 'Does quick_validate reject TODO placeholders everywhere, including code fences? Find description TODO detection, body fence handling, and the standalone-line test.',
 'validate TODO description placeholder fence body',[
 ('description','描述起始 TODO 拒绝','    if description.startswith("[TODO:"):',False),
 ('fence','跟踪 fence 起止','            elif (\n                marker[0] == fence_marker',True),
 ('body','只检查 fence 外匹配整行的 TODO','        if fence_marker is None and re.fullmatch(',True)])
# Fence exclusion requires both the condition and its completed state update.
cases[-1]['facts'][1]['evidence_alternatives']=[['creator-022','creator-023']]
dump('corpus.json',corpus);dump('samples.json',cases)
print('New corpus:',{k:len(v) for k,v in corpus.items()},'tasks=',len(cases))
