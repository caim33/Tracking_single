"""Generate/check a per-file tutorial and API index. See Deploy/docs/07_validation.md.

Run --write after reviewing corresponding stage guides; default checks drift.
This checks coverage and signatures, not the truth of hardware validation claims.
"""
import argparse
import ast
import hashlib
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / 'RL_envs/docs/code_reference.md'
DOCS = {
    '01_install.md': 'RL_envs/docs/01_install.md',
    '02_video.md': 'GVHMR/docs/02_video.md',
    '03_motion.md': 'GMR/docs/03_motion.md',
    '04_training.md': 'RL_envs/docs/04_training.md',
    '05_deploy.md': 'Deploy/docs/05_deploy.md',
    '06_real_robot.md': 'Deploy/docs/06_real_robot.md',
    '07_validation.md': 'Deploy/docs/07_validation.md',
}
SKIP = {'.git','__pycache__','.pytest_cache','.venv','outputs','logs','data','bundles'}
GUIDES = [
    ('Deploy/tests/','07_validation.md','动作转换和部署回归测试；按测试函数查看保护的行为'),
    ('Deploy/tools/','07_validation.md','维护全流程教程覆盖及检查记录'),
    ('Deploy/sim2real.py','06_real_robot.md','SDK2 单次动作发布、只读检查和停控'),
    ('Deploy/robot_state.py','06_real_robot.md','实测电机/IMU 到训练坐标系的转换'),
    ('Deploy/','05_deploy.md','单动作策略包、观测、PD 与仿真接口'),
    ('GMR/pipeline/','03_motion.md','命名动作、时间采样、四元数和正向运动学'),
    ('RL_envs/','04_training.md','tracking_single 的训练、配置与 MDP'),
    ('GVHMR/','02_video.md','人体恢复及其内部数学/网络模块'),
    ('GMR/','02_video.md','人体动作重定向、机器人模型及内部数学模块'),
]

def sources():
    return sorted(p for p in ROOT.rglob('*') if p.is_file() and not any(x in SKIP or x.endswith('.egg-info') for x in p.relative_to(ROOT).parts)
                  and p.suffix in ('.py','.h','.cpp','.sh'))

def guide_for(path):
    for prefix,guide,purpose in GUIDES:
        if path.startswith(prefix): return guide,purpose
    return '01_install.md','项目安装与环境定义'

def signature(node):
    if isinstance(node,ast.ClassDef):
        return f'class {node.name}('+', '.join(ast.unparse(x) for x in node.bases)+')'
    return f'{node.name}({ast.unparse(node.args)})'+(f' -> {ast.unparse(node.returns)}' if node.returns else '')

def render():
    code=sources()
    text=['# 逐文件教程与 API 参考','',f'本索引覆盖 **{len(code)} 个代码文件**。由 `python Deploy/tools/audit_docs.py --write` 生成并随代码提交。',
          '', '先阅读对应阶段教程完成环境、输入、运行、输出检查和排错，再进入函数或配置。库模块不应逐个直接运行。',
          'API 索引来自语法树；命令参数来自显式 add_argument 定义。动态框架参数在阶段教程解释。索引覆盖不等于 GPU/真机验收。','']
    for p in code:
        rel=p.relative_to(ROOT).as_posix(); guide,purpose=guide_for(rel)
        content=p.read_text(encoding='utf-8-sig')
        digest=hashlib.sha256(content.encode('utf-8')).hexdigest()[:12]
        source_link = Path(os.path.relpath(p, INDEX.parent)).as_posix()
        guide_link = Path(os.path.relpath(ROOT / DOCS[guide], INDEX.parent)).as_posix()
        text += [f'## `{rel}`','',f'[源码]({source_link}) · [使用教程]({guide_link}) · 内容指纹 `{digest}`','',f'职责：{purpose}。','']
        if p.suffix!='.py':
            text+=['使用方式：原 deploy 接口参考，当前 Python 单动作控制路径不直接编译此文件。依赖与替代入口见 deploy 教程。','']
            continue
        tree=ast.parse(content,filename=rel)
        doc=ast.get_docstring(tree)
        if doc:
            paragraph=doc.split('\n\n')[0].replace('\n',' ')
            text += [f'模块说明：{paragraph[:700]}','']
        symbols=[]
        for item in tree.body:
            if isinstance(item,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                symbols.append((signature(item),ast.get_docstring(item)))
                if isinstance(item,ast.ClassDef):
                    for method in item.body:
                        if isinstance(method,(ast.FunctionDef,ast.AsyncFunctionDef)):
                            symbols.append((item.name+'.'+signature(method),ast.get_docstring(method)))
        if symbols:
            text += ['接口与职责：','']
            for name,doc in symbols:
                detail=(doc.split('\n\n')[0].replace('\n',' ')[:350] if doc else '行为见对应阶段教程及源码。')
                text += [f'- `{name}` — {detail}']
            text += ['']
        else:
            names=[n.id for node in tree.body if isinstance(node,(ast.Assign,ast.AnnAssign)) for n in ([node.target] if isinstance(node,ast.AnnAssign) else node.targets) if isinstance(n,ast.Name)]
            text += ['使用方式：包注册、常量或参数配置，由上级模块导入。'+(' 顶层配置：'+', '.join(f'`{x}`' for x in names)+'.' if names else ''),'']
        options=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='add_argument':
                args=[a.value for a in node.args if isinstance(a,ast.Constant) and isinstance(a.value,str)]
                if args:
                    props={k.arg:ast.unparse(k.value) for k in node.keywords}
                    options.append((args,props))
        if options:
            text += ['命令行参数（运行所在目录与完整例子见上方教程）：','']
            for names,props in options:
                detail='; '.join(f'{k}={props[k]}' for k in ('required','default','choices','action','help') if k in props)
                text += [f'- `{", ".join(names)}`'+(' — '+detail if detail else '')]
            text += ['']
    return '\n'.join(line.rstrip() for line in text).rstrip()+'\n'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true',help='Regenerate code_reference.md after reviewing guides')
    args=parser.parse_args()
    expected=render(); path=INDEX
    if args.write:
        path.write_text(expected,encoding='utf-8',newline='\n')
    if not path.exists() or path.read_text(encoding='utf-8')!=expected:
        raise SystemExit('Code/tutorial index drift. Review guides, then run python Deploy/tools/audit_docs.py --write')
    errors=[]
    # Authored root/stage/index documents; retained third-party asset READMEs
    # may reference their full upstream repo and are attribution, not tutorials.
    pages=[ROOT/'README.md',ROOT/'THIRD_PARTY_NOTICES.md',
           ROOT/'GVHMR/README.md',ROOT/'GMR/README.md',
           ROOT/'RL_envs/README.md',ROOT/'Deploy/README.md',
           INDEX, *(ROOT / guide for guide in DOCS.values())]
    for page in pages:
        for link in re.findall(r'\]\(([^)]+)\)',page.read_text(encoding='utf-8')):
            if '://' in link or link.startswith('#'): continue
            target=link.split('#',1)[0]
            if target and not (page.parent/target).exists(): errors.append(f'{page.relative_to(ROOT)}: {link}')
    if errors: raise SystemExit('Broken documentation links:\n'+'\n'.join(errors))
    print(f'PASS: {len(sources())} code files indexed; authored documentation links resolve')

if __name__=='__main__':
    main()
