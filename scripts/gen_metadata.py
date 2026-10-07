#!/usr/bin/env python3
"""gen_metadata.py — command_metadata.json 唯一 metadata projection 生成器（架构重构批次 A）

评审 #112 P2: 命名修正——多 registry(ENGINE_REGISTRY/CLI_TOOLS/cli manual/bridges)
→ CommandSpec → metadata 投影。command_metadata.json 是唯一**投影**, 非唯一源。

合并事实来源 → 单一 metadata：
  1. ENGINE_REGISTRY（auto_commands.py 表驱动，172 命令）— 运行时权威
  2. 手动注册命令（cli.py @group.command，13 个）
  3. CLI_TOOLS（cli_tools_registry.py，82 工具）— 工具层
  4. bridges/*.java（118）— 桥索引

用法:
  python3 scripts/gen_metadata.py            # 生成（写 command_metadata.json + 打印断言）
  python3 scripts/gen_metadata.py --check    # 只校验一致性（CI/防漂移，不写文件）
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META = os.path.join(ROOT, "tbtools_cli", "command_metadata.json")
AUTO = os.path.join(ROOT, "tbtools_cli", "auto_commands.py")
CLI = os.path.join(ROOT, "tbtools_cli", "cli.py")
REG = os.path.join(ROOT, "tbtools_cli", "cli_tools_registry.py")
BRIDGES = os.path.join(ROOT, "bridges")


def scan_engine_registry():
    """运行时导入 ENGINE_REGISTRY（auto_commands 模块级列表，权威来源）"""
    sys.path.insert(0, ROOT)
    from tbtools_cli import auto_commands as ac
    cmds = {}
    for (name, kind, cls, xmx, runner, doc) in ac.ENGINE_REGISTRY:
        cmds[name] = {"name": name, "kind": kind, "mode": kind, "class": cls,
                      "xmx": xmx, "runner": runner, "help": doc[:400], "src": "engine_registry"}
    return cmds


def scan_cli_tools():
    sys.path.insert(0, ROOT)
    from tbtools_cli.cli_tools_registry import CLI_TOOLS
    tools = {}
    for name, cls in CLI_TOOLS.items():
        # 类名末段 → 人类可读标题(rpkmCal → "rpkmCal (RpkmCal)")
        short = cls.split(".")[-1] if isinstance(cls, str) else str(cls)
        pretty = re.sub(r"(?<!^)(?=[A-Z])", " ", short) if short else name
        tools[name] = {"name": name, "kind": "tool", "mode": "tool", "class": cls,
                       "xmx": "3g", "runner": "java",
                       "help": f"{name}: {name} (tool, {short}) — {pretty}", "src": "cli_tools_registry"}
    return tools


def scan_manual_commands():
    src = open(CLI, encoding="utf-8").read()
    cmds = {}
    # 1) 装饰器命令(顶层管理命令跳过)
    # 自审 v1.4.82 arch N4: KNOWN_TOP_MANUAL 单一来源——此前两份字面拷贝, 改一边漏一边
    # 会破 298=298 等价。从 command_spec 导入(真源)。
    from tbtools_cli.command_spec import KNOWN_TOP_MANUAL as _KNOWN_TOP_MANUAL
    for name in re.findall(r"@(?:\w+_group|\w+)\.command\(\s*['\"]([a-zA-Z][a-zA-Z0-9_-]*)['\"]", src):
        # 顶层 Agent/管理命令(非生信工具, 不进 metadata 模型; 含 09/23 新增 Agent 接口层)
        if name in _KNOWN_TOP_MANUAL:
            continue
        cmds[name] = {"name": name, "kind": "manual", "mode": "manual", "class": "",
                      "xmx": "", "runner": "plot", "help": "", "src": "cli_manual"}
    # 2) docstring 首行(跨 click 装饰器): 装饰器+def+docstring
    for m in re.finditer(
        r'@(?:\w+_group|\w+)\.command\(\s*[\"\']([a-zA-Z][a-zA-Z0-9_-]*)[\"\']\)'
        r'[\s\S]*?^def [a-zA-Z_][a-zA-Z0-9_]*\([^)]*\):\s*\"\"\"([^\"]{0,300})',
        src, re.M | re.S):
        cmd, d = m.group(1), m.group(2).strip()[:300]
        if cmd in cmds and d:
            cmds[cmd]["help"] = d
    # 3) auto_commands 手写 impl(N23/N26 后 msy/mirnatarget 等必须可发现)
    try:
        ac_src = open(os.path.join(os.path.dirname(CLI), "auto_commands.py"), encoding="utf-8").read()
        for m in re.finditer(r"^def _([a-zA-Z0-9]+)_impl\([^)]*\):\s*\"\"\"([^\"]{0,300})", ac_src, re.M | re.S):
            name, docfirst = m.group(1), m.group(2).strip()
            if name in cmds or name in ("simplehmmscan", "longestorf"):
                continue
            cmds[name] = {"name": name, "kind": "manual", "mode": "manual", "class": "",
                          "xmx": "", "runner": "plot", "help": docfirst[:300], "src": "auto_manual"}
    except Exception as _e85:
        # gate P2-1: manual 扫描失败 → 该批命令静默消失(arch N6 同源), 可见化
        print(f"⚠️ 告警: auto_commands 源码扫描失败, manual 命令可能缺失: {_e85}", file=sys.stderr)
    for m in re.finditer(r"(\w+_group)\.add_command\((\w+),\s*name=[\"']([a-zA-Z][a-zA-Z0-9_]*)[\"']\)", src):
        fn, alias = m.group(2), m.group(3)
        if alias not in cmds:
            cmds[alias] = {"name": alias, "kind": "manual", "mode": "manual", "class": "",
                           "xmx": "", "runner": "plot", "help": "", "src": "cli_manual"}
        if not cmds[alias].get("help"):
            # 函数名→命令名: 分组前缀去除 + 已知特例(seqlogo 函数 → logo 命令)
            target = {"seqlogo": "logo"}.get(fn, fn)
            for _p in ("seq_", "expr_", "tree_", "tool_", "gene_"):
                if target.startswith(_p):
                    target = target[len(_p):]
                    break
            if target in cmds and cmds[target].get("help"):
                cmds[alias]["help"] = f"(alias of {target}) " + cmds[target]["help"]
            elif fn in cmds and cmds[fn].get("help"):
                cmds[alias]["help"] = f"(alias of {fn}) " + cmds[fn]["help"]
    return cmds


def scan_bridges():
    return sorted(f[:-5] for f in os.listdir(BRIDGES) if f.endswith(".java"))


def _infer_group(name, kind, src=""):
    """命令分组推断(CATEGORY_MAP 优先, kind/src 兜底)"""
    try:
        sys.path.insert(0, ROOT)
        from tbtools_cli.cli_load import CATEGORY_MAP as _CM
        if name in _CM:
            return _CM[name]
    except Exception as _e118:
        # gate P2-1: CATEGORY_MAP 不可用 → 分组推断降级到 kind/src 兑底, 可见化
        print(f"⚠️ 告警: CATEGORY_MAP 导入失败, 分组推断降级: {_e118}", file=sys.stderr)
    if kind == "tool":
        return "tool"
    if kind == "manual":
        # cli.py 装饰器分组: @expr_group.command("volcano") → expr
        try:
            cli_src = open(CLI, encoding="utf-8").read()
            m = re.search(r'@(\w+_group)\.command\(\s*["\']' + re.escape(name) + r'["\']', cli_src)
            if m:
                grp = m.group(1)[:-6]  # expr_group → expr
                return grp
        except Exception as _e130:
            # gate P2-1: 源码正则分组推断失败 → 回退 engine 分组, 可见化
            print(f"⚠️ 告警: 分组源码扫描失败({name}), 回退 engine: {_e130}", file=sys.stderr)
    return "engine"


def _build_specs(reg, tools, manual):
    """扫描结果 → CommandSpec 模型 → metadata 投影(复用 command_spec 单一组装逻辑)"""
    sys.path.insert(0, ROOT)
    from tbtools_cli.command_spec import specs_from_scans
    return specs_from_scans(reg, tools, manual, infer_group=_infer_group)




def build():
    reg = scan_engine_registry()
    tools = scan_cli_tools()
    manual = scan_manual_commands()
    bridges = scan_bridges()

    # 模型接管(二期): 扫描 → CommandSpec 统一模型 → metadata 投影(完全重建, 无残影)
    meta = _build_specs(reg, tools, manual)
    # tree 分组别名（显示名 ≠ 函数名）: draw→tree, one-step→onesteptree, rooting→treeRooting
    for alias, disp in (("tree", "draw"), ("onesteptree", "one-step"), ("treeRooting", "rooting")):
        if alias not in meta and disp in meta:
            # 自审红队 P1-1: 别名特判改为从 CommandSpec 模型投影(而非手工 dict)——
            # 确保 dependency_manifest 等展开与 build_command_specs 完全一致(单一投影源)
            try:
                from tbtools_cli.command_spec import (CommandSpec,
                                                      KNOWN_DEPENDENCIES as _kd2,
                                                                                                            KNOWN_STATUS as _kst2)
                _alias_spec = CommandSpec(
                    name=alias, group=meta[disp].get("group", "engine"), kind="manual",
                    runner="plot", doc=meta[disp].get("help", ""), alias_of=disp,
                )
                _alias_spec.status = _kst2.get(alias, "stable")
                # 名字列表(与 build_command_specs 侧一致): manifest 由 to_metadata_entry
                # 从 STRUCT 展开——设 STRUCT dict 列表会与 spec 侧展开撞车
                _alias_spec.dependencies = list(_kd2.get(alias) or _kd2.get(disp) or [])
                _alias_spec.capabilities = meta[disp].get("capabilities") or []
                _alias_spec.relations = meta[disp].get("relations") or {}
                from tbtools_cli.command_spec import to_metadata_entry as _tme2
                meta[alias] = _tme2(_alias_spec)
            except Exception as _e_alias:
                # 自审 arch N6: 删除手工 dict 双轨兜底——import 失败就该 build 失败,
                # 静默降级成结构不同产物(缺 semantic_fingerprint/schema 等模型展开)
                # 会让别名工具 Agent 面不自洽(双轨残留根除)
                raise RuntimeError(
                    f"别名 {alias}→{disp} 模型投影失败, 拒绝静默降级: {_e_alias}") from _e_alias

    # 兜底: 旧 metadata 遗留条目统一补 kind（兼容历史数据）
    for _v in meta.values():
        _v.setdefault("kind", "manual")
        _v.setdefault("mode", "manual")
    # 二期: 统一补 group 字段(直接可查, 无需运行时推断)
    for _n, _v in meta.items():
        _v.setdefault("group", _infer_group(_n, _v.get("kind", "manual"), _v.get("src", "")))
    # Agent-ready 统计(评审 #64: FULL/PARTIAL/LEGACY 自动统计进 counts)
    try:
        from tbtools_cli.command_spec import readiness_census as _rc
        _census = _rc()
    except Exception:
        _census = {}
    # Contract Coverage(评审 #72 P2-1): 契约完备度统计
    try:
        from tbtools_cli.command_spec import KNOWN_NAMED_FLAGS, build_command_specs as _bcs_cov
        _spc = _bcs_cov()
        _cov = {"total": len(_spc),
                "with_inputs": sum(1 for s in _spc.values() if s.inputs),
                "with_outputs": sum(1 for s in _spc.values() if s.outputs),
                "with_parameters": sum(1 for s in _spc.values() if s.parameters),
                "with_capabilities": sum(1 for s in _spc.values() if s.capabilities),
                "with_relations": sum(1 for s in _spc.values() if s.relations),
                "invocation_compilable": sum(1 for s in _spc.values()
                                           if s.inputs or s.name in KNOWN_NAMED_FLAGS)}
    except Exception:
        _cov = {}
    counts = {"registry": len(reg), "tools": len(tools), "bridges": len(bridges),
              "meta_total": len(meta),
              "plot_ish": sum(1 for v in meta.values() if v.get("kind") in ("bridge", "direct", "manual")),
        "agent_ready_full": _census.get("FULL", 0),
        "agent_ready_partial": _census.get("PARTIAL", 0),
        "agent_ready_legacy": _census.get("LEGACY", 0),
        "contract_coverage": _cov}
    return meta, counts


def render_commands_md(meta, out_root: str | None = None) -> set:
    """按分组生成全量命令清单 docs/_generated/commands.md（metadata 驱动,防漂移）。

    out_root(评审 #114 P0-2): 渲染根目录——--check 传临时目录实现完全只读检查;
    默认 ROOT(正式写盘)。返回写过的相对路径集(评审 #114 P1-4: Gate 自动覆盖,
    不再手工维护 surface 白名单)。"""
    import sys as _sys2
    _sys2.path.insert(0, ROOT)
    from tbtools_cli.cli_load import CATEGORY_MAP, GROUPS
    _out_root = out_root or ROOT
    out_dir = os.path.join(_out_root, "docs", "_generated")
    os.makedirs(out_dir, exist_ok=True)
    _written: set = set()
    lines = ["# 命令全量清单（自动生成,勿手改）",
             "",
             "> 由 `python3 scripts/gen_metadata.py --render` 生成,来源 command_metadata.json。",
             "> 分组归类参考 cli_load.CATEGORY_MAP;数字防漂移由 gen_metadata.py --check 与 pytest 保证。",
             ""]
    # 分组 → 命令
    grouped: dict[str, list] = {}
    for name, v in meta.items():
        cat = CATEGORY_MAP.get(name, "engine")
        grouped.setdefault(cat, []).append((name, v))
    for cat in sorted(GROUPS.keys()):
        if cat not in grouped:
            continue
        cmds = grouped[cat]
        lines.append(f"## {cat} — {GROUPS.get(cat, cat)}（{len(cmds)} 个）")
        lines.append("")
        lines.append("| 命令 | 类型 | 说明 |")
        lines.append("|---|---|---|")
        for name, v in sorted(cmds):
            kind = v.get("kind", "?")
            icon = {"bridge": "桥", "direct": "直连", "tool": "工具", "manual": "手动"}.get(kind, kind)
            desc = (v.get("help", "") or "").split("#")[-1].strip() or (v.get("help", "") or "")[:40]
            if ":" in desc:
                desc = desc.split(":", 1)[-1].strip()
            # 自审 product F6: 按词边界截断(原 desc[:60] 硬切出半词 [sor 瑕疵)
            desc = desc if len(desc) <= 60 else (desc[:61].rsplit(" ", 1)[0] + "…" if " " in desc[:61] else desc[:60] + "…")
            lines.append(f"| `{name}` | {icon} | {desc} |")
        lines.append("")
    # 数字统计(权威口径)
    from collections import Counter
    kinds = Counter(v.get("kind", "?") for v in meta.values())
    lines.append("## 统计")
    lines.append("")
    lines.append(f"- 命令总数: {len(meta)}")
    for k, n in kinds.most_common():
        lines.append(f"- {k}: {n}")
    lines.append("")
    path = os.path.join(out_dir, "commands.md")
    open(path, "w", encoding="utf-8").write("\n".join(lines))
    _written.add(os.path.relpath(path, _out_root))
    print(f"✅ 已生成 {os.path.relpath(path, ROOT)}（{len(meta)} 命令,{len(lines)} 行）")

    # 权威数字摘要(README/徽章/文档口径单一源)
    import tbtools_cli.auto_commands as _ac
    import tbtools_cli.core as _core
    n_plot = sum(1 for v in meta.values() if v.get("kind") in ("bridge", "direct", "manual"))
    n_auto = sum(1 for n in dir(_ac) if n.startswith("_") and n.endswith("_impl") and not n.startswith("__"))
    from tbtools_cli.command_spec import build_command_specs as _bcs_specs  # P2-1: 与 version --json 同源
    counts = {
        "metadata_commands": len(meta),          # 298: 唯一数据源全量(动态, 勿硬编码)
        "metadata_plot_commands": n_plot,        # 218: metadata 静态口径(非工具类 bridge/direct/manual, 动态)
        "auto_commands": n_auto,                 # 201: 引擎注册表驱动的命令数
        # 自审 v1.4.85 gate P2-2: rpc_methods 注明口径——188 是 TBtools JAR 内置
        # RPC 方法数(外部引擎能力, 本地无注册源可动态统计), 硬编码有正当理由;
        # 已标注来源防被误当"可派生数字"。变更需随 JAR 升级人工核对。
        "rpc_methods": 188,  # 来源: TBtools_JRE1.6.jar RPC 服务器(外部能力, 非本地注册表)
        # 自审 v1.4.83 product P2-1: tools 计数统一为 spec kind=="tool" 口径
        # (与 version --json 一致)——此前 counts.md 用 len(CLI_TOOLS)=82, version --json
        # 用 specs kind=="tool"=80, 两个权威自动源互相矛盾; 191 是人读页脚残留口径。
        "tools": sum(1 for s in _bcs_specs().values() if s.kind == "tool"),  # 80: 与 version --json 同源
        "bridges": len([f for f in os.listdir(os.path.join(ROOT, "bridges")) if f.endswith(".java")]),  # 118
        "pitfall_hints": len(_core.PITFALL_HINTS),  # 49: 动态
    }
    # 评审 #110 P1: counts.md 成为 agent-ready 权威口径(README 数字以此对齐, 防 59/60 漂移)
    try:
        from tbtools_cli.command_spec import readiness_census as _rc2, verification_census as _vc2
        _rd = _rc2()
        counts["agent_ready_full"] = _rd.get("FULL", 0)
        counts["agent_ready_partial"] = _rd.get("PARTIAL", 0)
        counts["agent_ready_legacy"] = _rd.get("LEGACY", 0)
        counts["execution_verified"] = _vc2().get("EXECUTION_VERIFIED", 0) + _vc2().get("CONFORMANCE_VERIFIED", 0)  # 评审 #111 P0-3: 统一口径=有真实执行证据的工具数
        counts["conformance_verified"] = _vc2().get("CONFORMANCE_VERIFIED", 0)
        # 自审 v1.4.82 verified N4(P2): semantic_checked 动态计数进权威数字——
        # 此前 README "10" 是手写静态文本, counts.md 不含该数, SEMANTIC_CHECKS 增删
        # 一条就静默漂移(P1-4 "动态口径"落点)。从 verification_report 的
        # verified_tools(单层 evidence map, canonical)实时统计。
        try:
            _vrp2 = os.path.join(ROOT, "tests", "verification_report.json")
            if os.path.isfile(_vrp2):
                _vrd2 = json.load(open(_vrp2, encoding="utf-8"))
                _vt2 = _vrd2.get("verified_tools") or {}
                counts["semantic_checked"] = sum(1 for e in _vt2.values() if e.get("semantic_checked"))
            else:
                counts["semantic_checked"] = 0
        except Exception as _e325:
            counts["semantic_checked"] = 0
            # gate P2-1: semantic_checked census 读取失败 → 静默报 0(与 _verif_n="?" 同源), 可见化
            print(f"⚠️ 告警: semantic_checked census 读取失败, 报 0: {_e325}", file=sys.stderr)
    except Exception as _e325b:
        # gate P2-1: verified_tools census 整体读取失败 → 静默降级, 可见化
        print(f"⚠️ 告警: verification census 读取失败(counts 降级): {_e325b}", file=sys.stderr)
    # 注(评审 #112): 两个绘图命令口径都合法勿互改——
    #   metadata_plot_commands(本文件): metadata 静态注册口径
    #   runtime 分组命令数: `tbtools version --json` 的 cli_commands(运行时全部分组,含 engine)
    counts_path = os.path.join(out_dir, "counts.md")
    with open(counts_path, "w", encoding="utf-8") as f:
        f.write("# 权威数字(自动生成,勿手改)\n\n")
        for k, v in counts.items():
            f.write(f"- {k}: {v}\n")
    _written.add(os.path.relpath(counts_path, _out_root))
    print(f"✅ 已生成 {os.path.relpath(counts_path, ROOT)}: {counts}")
    return _written


def _surface_hash(rel: str, path: str) -> str:
    """Generated surface 内容哈希——JSON 结构忽略 verified_at(测试运行元数据,
    每次 conformance 刷新, 非契约内容; 防时间戳变化致 --check 恒定假阳性,
    2026-10-04 实测 19:22→19:26 同一契约仅时间戳刷新)。非 JSON 文件整字节哈希。"""
    import hashlib as _hl
    import json as _j
    if rel.endswith(".json"):
        try:
            with open(path, encoding="utf-8") as _f:
                _o = _j.load(_f)

            def _strip(_x):
                if isinstance(_x, dict):
                    return {_k: _strip(_v) for _k, _v in _x.items() if _k != "verified_at"}
                if isinstance(_x, list):
                    return [_strip(_i) for _i in _x]
                return _x

            _s = _j.dumps(_strip(_o), sort_keys=True, ensure_ascii=False)
            return _hl.sha256(_s.encode("utf-8")).hexdigest()
        except Exception as _e360:
            # gate P2-1: JSON 结构化哈希失败 → 回退整字节(不再忽略 verified_at, 漂移检测变保守), 可见化
            print(f"⚠️ 告警: surface JSON 解析失败({rel}), 回退整字节哈希: {_e360}", file=sys.stderr)
    return _hl.sha256(open(path, "rb").read()).hexdigest()


def main():
    check = "--check" in sys.argv or "-c" in sys.argv
    render = "--render" in sys.argv or "-r" in sys.argv
    meta, counts = build()
    print(json.dumps(counts, ensure_ascii=False, indent=1))
    if check:
        # 评审 #114 P0-2(Generated Surface Gate v2): --check **完全只读**——
        # 渲染到临时目录, 与仓库现有 generated surfaces 对比(绝不修改工作树)。
        # 评审 #114 P1-4: 用 renderer 自报的 written set(不再手工维护 _surfaces 白名单)。
        import tempfile as _tf
        _tmp = _tf.mkdtemp(prefix="genmeta_check_")
        try:
            # 1) 渲染到临时目录(out_root), 收集 renderer 自报的全部 generated 相对路径
            _written = set()
            _written |= render_commands_md(meta, out_root=_tmp)
            _written |= render_ai_manifest(meta, out_root=_tmp)
            _json_dump(meta, out_root=_tmp)
            _written.add("tbtools_cli/command_metadata.json")
            _written.add("tbtools_cli/command_metadata.fingerprint.json")  # arch N8: sidecar 同盘进对比
            # 注: tests/verification_report.json 是测试产物(pytest 生成), 非 gen_metadata
            # render 的 surface——它被 render 读作输入, 不入 _written
            # 2) 逐个对比: 临时目录生成的 vs 仓库现有 —— 内容不同/缺失 = 漂移
            _drifted = []
            for _rel in sorted(_written):
                _fresh = os.path.join(_tmp, _rel)
                _repo = os.path.join(ROOT, _rel)
                if not os.path.isfile(_repo):
                    _drifted.append(f"(缺失) {_rel}")
                    continue
                _fb = _surface_hash(_rel, _fresh)
                _rb = _surface_hash(_rel, _repo)
                if _fb != _rb:
                    _drifted.append(_rel)
            # P0-2 自指陷阱修复(自审 gate F2): renderer 自报的 _written 只含"生成成功"的文件——
            # render 中途崩掉会少生成 → 旧文件不进对比集 → --check 反而报全同步(崩得越多越绿)。
            # 补 repo→fresh 方向: git 跟踪的全部 generated surface 必须在 fresh 里也存在。
            import subprocess as _sp2
            try:
                _git_surfaces = _sp2.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
            except Exception:
                _git_surfaces = []
            _gen_prefixes = ("ai/", "docs/_generated/", "tbtools_cli/command_metadata.json", "counts.md")
            for _rel in _git_surfaces:
                if not _rel.startswith(_gen_prefixes):
                    continue
                if _rel.endswith(".min.py"):  # ast_minfy 产物, 非 gen_metadata surface
                    continue
                if not os.path.isfile(os.path.join(_tmp, _rel)):
                    _drifted.append(f"(render 缺失) {_rel}")
            # 3) 动态 verification 数(评审 #114 P1-3: 不硬编码 44)
            try:
                from tbtools_cli.command_spec import verification_census as _vc3
                _vc = _vc3()
                _verif_n = _vc.get("EXECUTION_VERIFIED", 0) + _vc.get("CONFORMANCE_VERIFIED", 0)
            except Exception:
                _verif_n = "?"
            # 自审 v1.4.87 gate P2-1: census 静默降级告警——verification 数变 "?" 时
            # --check 不能报"全同步"(数字可信度是 EXECUTION_VERIFIED 叙事的一部分)
            if _verif_n == "?":
                print("⚠️ 警告: verification census 读取失败, execution_verified 数字不可信(降级为 '?')", file=sys.stderr)
            if _drifted:
                print(f"❌ Generated Surface 漂移: {len(_drifted)} 个文件与最新 source 不一致(未 render/提交):")
                for _line in _drifted[:15]:
                    print(f"   {_line}")
                print("   请运行 python3 scripts/gen_metadata.py --render 并提交所有 generated surface 后重试")
                return 1
            # 评审 #115 预审 P1-2(D2) 响应: verified_at 软 TTL——验证超过 90 天
            # 只 WARNING 不 fail(保留新鲜度信号但不扰门禁); 契约/引擎不变时
            # 时间戳冻结属设计语义, TTL 提醒"该考虑环境漂移了"。
            # 自审 gate P1-5: 软告警升级——TBTOOLS_TTL_STRICT=1(nightly-e2e)时 >90 天
            # 直接 fail(nightly 有真实 JAR 应回写保鲜; 超龄 = 保鲜机制失效 → 红)。
            _ttl_strict = os.environ.get("TBTOOLS_TTL_STRICT") == "1"
            try:
                _vp2 = os.path.join(ROOT, "tests", "verification_report.json")
                if os.path.isfile(_vp2):
                    import datetime as _dt2
                    _vt = json.load(open(_vp2, encoding="utf-8")).get("verified_tools") or {}
                    _old_days = []
                    _now2 = _dt2.datetime.now()
                    for _t2, _v2 in _vt.items():
                        _va = _v2.get("verified_at", "")
                        if _va:
                            try:
                                _age = (_now2 - _dt2.datetime.fromisoformat(_va)).days
                                if _age > 90:
                                    _old_days.append((_t2, _age))
                            except Exception:
                                pass  # 单条 verified_at 解析失败 → 该条 TTL 检查跳过(可容忍, 下轮再查)
                        _msg = (f"❌ 验证超龄 {len(_old_days)} 个(>90 天, TTL 严格模式阻断): "
                                + ", ".join(f"{t}({d}d)" for t, d in sorted(_old_days, key=lambda x: -x[1])[:8]))
                        if _ttl_strict:
                            print(_msg)
                            print("   —— nightly 应已回写保鲜; 超龄说明保鲜失效, 需人工重验", file=sys.stderr)
                            return 1
                        print(f"⚠️ 验证超龄({len(_old_days)} 个 >90 天, 软告警不阻断): "
                              + ", ".join(f"{t}({d}d)" for t, d in sorted(_old_days, key=lambda x: -x[1])[:8]))
            except Exception:
                # 自审 gate P1-2: TTL 检查异常不再静默——strict 模式下显式报错
                # (此前整块 try-except-pass 吞异常, TBTOOLS_TTL_STRICT 存在静默失效路径)
                if os.environ.get("TBTOOLS_TTL_STRICT") == "1":
                    print("❌ TTL 检查异常(TBTOOLS_TTL_STRICT=1 下视为失败): 无法读取 verification_report", file=sys.stderr)
                    return 1
            # 自审 docs F1/F3(gate P0-3) 版本门禁: pyproject version == 最新 git tag == README 声称线
            import re as _re2
            import subprocess as _sp3
            try:
                _py_m = _re2.search(r'^version = "([^"]+)"',
                                     open(os.path.join(ROOT, "pyproject.toml"), encoding="utf-8").read(), _re2.M)
                _py_ver = _py_m.group(1) if _py_m else ""
                _git_tags = _sp3.check_output(["git", "tag"], cwd=ROOT, text=True).splitlines()
                _latest_tag = sorted((t for t in _git_tags if t.startswith("v")), key=lambda t: [int(x) for x in t[1:].split(".")])
                _latest = _latest_tag[-1][1:] if _latest_tag else ""
                _readme_txt = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
                _ver_lt = [int(x) for x in _py_ver.split(".")] if _py_ver else []
                _tag_lt = [int(x) for x in _latest.split(".")] if _latest else []
                # 允许 pyproject 领先 tag(待发状态), 仅拦"落后漂移"(发了版没 bump)
                if _ver_lt and _tag_lt and _ver_lt < _tag_lt:
                    print(f"❌ 版本漂移: pyproject={_py_ver} < 最新 tag={_latest}——发版必须同步 bump")
                    return 1
                if _ver_lt and f"v{_py_ver}" not in _readme_txt:
                    print(f"❌ README 未提当前版本 v{_py_ver}——文档与发布线脱节")
                    return 1
                print(f"✅ 版本一致性: pyproject={_py_ver} (tag v{_latest}) && README 含 v{_py_ver}")
            except Exception as _e4:
                print(f"⚠️ 版本门禁不可用(非阻断): {_e4}", file=sys.stderr)
            print(f"✅ Generated Surface 一致性: {len(meta)} 命令 / verification={_verif_n} / "
                  f"{len(_written)} 个 surface 全同步(只读检查未写盘)")
            return 0
        finally:
            import shutil as _sh2
            _sh2.rmtree(_tmp, ignore_errors=True)
    _json_dump(meta)
    print(f"✅ 已写入 {META}: {len(meta)} 命令")
    if render:
        render_commands_md(meta)
        render_ai_manifest(meta)
    return 0


def _json_dump(meta, out_root: str | None = None):
    """写 command_metadata.json(唯一写盘点; out_root 供 --check 临时渲染)."""
    import json as _j
    _p = (out_root or ROOT) + "/tbtools_cli/command_metadata.json"
    _os_d = os.path.dirname(_p)
    if not os.path.isdir(_os_d):
        os.makedirs(_os_d, exist_ok=True)
    with open(_p, "w", encoding="utf-8") as _f:
        _j.dump(meta, _f, ensure_ascii=False, indent=1)
    # 自审 arch N8: 投影 staleness 守卫 sidecar(与 command_metadata.json 同写盘点)——
    # 消费端(tool-describe/tool-run 等)读投影前比对源码 mtime 指纹, 改源码未重跑
    # render → warn, 不再静默吃旧数据(yaml 快照比对机制延伸到 JSON 投影)
    try:
        from tbtools_cli.meta_guard import write_fingerprint
        write_fingerprint(out_root)
    except Exception:
        pass  # sidecar 不可写不阻断(守卫缺失=无对比基准, 不打扰)

def _clip_words(text: str, limit: int) -> str:
    """词边界截断(自审 product P2-5): limit 处不断半词; 顺带清理 usage 噪音
    (|None]/[ 残片)进 description。"""
    import re as _r
    _clean = _r.sub(r"\|None\]|#|\[", "", text)
    _clean = _r.sub(r"\s+", " ", _clean).strip()
    if len(_clean) <= limit:
        return _clean
    if " " not in _clean[:limit + 1]:
        return _clean[:limit] + "…"
    return _clean[:limit + 1].rsplit(" ", 1)[0] + "…"


def render_ai_manifest(meta, out_root: str | None = None) -> set:
    """AI 机器接口层(ai/): 工具索引/能力索引/单工具 schema/错误码(GLM P1 #38-39)。

    由 gen_metadata --render 统一生成, 与 metadata 单一数据源联动。
    out_root(评审 #114 P0-2): --check 传临时目录实现只读检查; 默认 ROOT。
    返回写过的相对路径集(Gate 自动覆盖, 不再手工维护 surface 白名单)。
    """
    import json as _json
    import os as _os
    _out_root = out_root or ROOT
    ai_dir = _os.path.join(_out_root, "ai")
    _written: set = set()
    # 评审 #112 P1: verification 证据详情(从 tests/verification_report.json 读)
    # ——ai/tools/*.json 的 verification_details 投影来源
    _verif_details_map: dict = {}
    try:
        _vp = _os.path.join(ROOT, "tests", "verification_report.json")
        if _os.path.isfile(_vp):
            _vd = _json.load(open(_vp, encoding="utf-8"))
            _verif_details_map = _vd.get("verified_tools") or _vd.get("execution_verified_details") or {}  # 评审 #114: verified_tools canonical
    except Exception as _e547:
        # gate P2-1: verification report 读取失败 → ai/tools 投影丢 evidence(静默), 可见化
        print(f"⚠️ 告警: verification_report.json 读取失败, ai/tools 无 verification_details: {_e547}", file=sys.stderr)
    _os.makedirs(_os.path.join(ai_dir, "tools"), exist_ok=True)
    import shutil as _sh
    for _sub in _os.listdir(_os.path.join(ai_dir, "tools")):
        _sh.rmtree(_os.path.join(ai_dir, "tools", _sub), ignore_errors=True)  # 防残影(与 metadata 全重建一致)
    with open(_os.path.join(ai_dir, "tool-index.jsonl"), "w", encoding="utf-8") as f:
        for name, v in meta.items():
            _inputs = v.get('inputs') or []
            _caps = v.get('capabilities') or []
            # 自审 product F6: 无契约命令显式 schema:null(空数组语义="无输入"还是"未知"?
            # 对 LEGACY/PARTIAL 无契约者, Agent 不该把 [] 当"可跑无参"——显式 null 表示未知)
            _has_contract = bool(_inputs or _caps or v.get('parameters'))
            entry = {"id": f"tbtools.{v.get('group','engine')}.{name}",
                     "uri": f"tbtools://{v.get('group','engine')}/{name}", "name": name,
                     "group": v.get('group', 'engine'), "kind": v.get('kind', '?'),
                     "alias_of": v.get('alias_of', ""), "capabilities": _caps,
                     "input_formats": sorted({i.get('format','') for i in _inputs if i.get('format')}),
                     "output_formats": v.get('outputs', []),
                     # 自审 v1.4.85 product P2-5: description 词边界截断(原 [:160]
                     # 硬切出半词 + usage 噪音; 与 commands.md F6 同策略)
                     "description": _clip_words((v.get('help','') or '').replace('\n', ' '), 160),
                     "schema": None if not _has_contract else "tool_schema_v1",  # F6: 无契约显式 null
                     # 评审 #112 P1: 低体积高价值筛选字段——Agent 搜索后可直接按证据强度过滤,
                     # 不必逐个 describe
                     "readiness": v.get('readiness', ''), "verification": v.get('verification', ''),
                     "semantic_fingerprint": v.get('semantic_fingerprint', '')}
            f.write(_json.dumps(entry, ensure_ascii=False) + '\n')
    cap_idx: dict[str, list] = {}
    for name, v in meta.items():
        for c in v.get('capabilities', []):
            cap_idx.setdefault(c, []).append(name)
    _json.dump(cap_idx, open(_os.path.join(ai_dir, "capability-index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for name, v in meta.items():
        g = v.get('group', 'engine')
        d = _os.path.join(ai_dir, "tools", g)
        _os.makedirs(d, exist_ok=True)
        schema = {"schema_version": "1.0", "id": f"tbtools.{g}.{name}", "name": name, "group": g,
                  "kind": v.get('kind', '?'), "class": v.get('class', ''),
                  "description": (v.get('help','') or '').split('#')[-1].strip(),
                  "invoke": f"tbtools {g} {name} <args...>" if g != 'engine' else f"tbtools engine {v.get('class','')} key=value",
                  "capabilities": v.get('capabilities', []), "inputs": v.get('inputs', []),
                  "outputs": v.get('outputs', []), "status": v.get('status', 'stable')}
        # 评审 #112 P1: AI manifest 与 CommandSpec metadata 统一投影——trust 字段补齐,
        # 防"tool-describe 信息完整 / ai/*.json 被削薄"双世界分裂
        for _k in ("semantic_fingerprint", "semantic_fingerprint_short", "readiness", "verification",
                   "relations", "output_slots", "parameters", "dependencies", "dependency_manifest",
                   "aliases"):
            if v.get(_k):
                schema[_k] = v[_k]
        # 评审 #112 P1: verification 证据对象投影——Agent 看到的不只是 level(EXECUTION_VERIFIED),
        # 还有绑定证据(验证时间/语料/契约指纹), 可判断证据新旧/是否匹配当前 contract
        _verif_details = _verif_details_map.get(name)
        # 自审 v1.4.86 verified N2: 顶层 verification 与嵌套 details.level 分叉时**不投影**
        # 过期证据——加载侧 _load_verification_report 有 contract_fp/env_fp 双比对(失配即
        # 降级), 契约变更后重跑验证前的窗口期, metadata 的 verification 已是降级值而 report
        # 仍是旧证据; 若此时仍无条件挂 details, 同一文件会并存 verification:COMPILEABLE +
        # verification_details.level:EXECUTION_VERIFIED, 自相矛盾。对齐降级语义: level 失配
        # 即视为证据失效不投影(消费者可经 contract_fingerprint 自行比对)。
        _vd_level = (_verif_details or {}).get("level", "")
        if _verif_details and _vd_level == v.get("verification", ""):
            # 自审红队 P1-3: 完整投影验证证据——Agent 需要区分"跑过" vs "跑过+内容级检查"
            # (semantic_checked) + 环境身份(env_fingerprint) + 验证域(domain_note)
            schema["verification_details"] = {
                "level": _verif_details.get("level", ""),
                "contract_fingerprint": _verif_details.get("contract_fingerprint", ""),
                "env_fingerprint": _verif_details.get("env_fingerprint", ""),
                "verified_at": _verif_details.get("verified_at", ""),
                "corpus": _verif_details.get("corpus", ""),
                "semantic_checked": bool(_verif_details.get("semantic_checked", False)),
                "domain_note": _verif_details.get("domain_note", ""),
            }
        _json.dump(schema, open(_os.path.join(d, f"{name}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    try:
        from tbtools_cli.core import ERROR_CODES
        _json.dump(ERROR_CODES, open(_os.path.join(ai_dir, "error-codes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    except Exception as _e1:
        print(f"⚠️ gen_metadata: error-codes.json 写盘失败: {_e1}", file=sys.stderr)  # 自审 gate P0-2: 静默 except 可见化
    workflows = [
        {"id": "gene-family-analysis", "title": "基因家族分析(GRAS 实测)",
         "steps": [{"tool": "muscle", "role": "msa"}, {"tool": "trimal", "role": "trim"},
                   {"tool": "iqtree", "role": "phylogeny"}, {"tool": "motif", "role": "motif"},
                   {"tool": "genestructure", "role": "gene_structure"}],
         "inputs": [{"name": "family_fasta", "type": "fasta"}],
         "outputs": ["aln", "nwk", "svg"]},
        {"id": "rna-seq", "title": "RNA-seq 差异分析",
         "steps": [{"tool": "tpmCalc", "role": "normalize"}, {"tool": "pca", "role": "qc"},
                   {"tool": "heatmap", "role": "viz"}, {"tool": "volcano", "role": "deg"}],
         "inputs": [{"name": "counts", "type": "tsv"}, {"name": "len_info", "type": "tsv"}],
         "outputs": ["tsv", "svg"]},
        {"id": "comparative-genomics", "title": "比较基因组学(共线性)",
         "steps": [{"tool": "mcscanx", "role": "collinearity"}, {"tool": "dualsyn", "role": "viz"},
                   {"tool": "dotplot", "role": "viz"}],
         "inputs": [{"name": "gff", "type": "gff3"}, {"name": "blast", "type": "tsv"}],
         "outputs": ["collinearity", "svg"]},
        {"id": "phylogeny", "title": "系统发育",
         "steps": [{"tool": "msa", "role": "align"}, {"tool": "trimal", "role": "trim"},
                   {"tool": "onesteptree", "role": "phylogeny"}, {"tool": "tree", "role": "draw"}],
         "inputs": [{"name": "fasta", "type": "fasta"}],
         "outputs": ["nwk", "svg"]},
    ]
    try:
        from tbtools_cli.command_spec import build_command_specs as _bcs_rel
        # 评审 #112 P1: relations.json 从 CommandSpec 派生(含 GROUP_RELATIONS fallback)——
        # 此前直读 KNOWN_RELATIONS, 只依赖 group 兜底的工具在 ai/relations.json 缺失(双轨)
        _rels_all = {}
        for _n, _sp in _bcs_rel().items():
            if _sp.relations:
                _rels_all[_n] = dict(_sp.relations)
        _json.dump({"schema_version": "1.0", "relations": _rels_all},
                   open(_os.path.join(ai_dir, "relations.json"), "w", encoding="utf-8"),
                   ensure_ascii=False, indent=1)
    except Exception as _e659:
        # gate P2-1: relations.json 导出失败 → Agent 关系面缺失(静默), 可见化
        print(f"⚠️ 告警: relations.json 导出失败, Agent 关系面缺失: {_e659}", file=sys.stderr)
    _json.dump({"schema_version": "1.0", "workflows": workflows},
               open(_os.path.join(ai_dir, "workflows.json"), "w", encoding="utf-8"),
               ensure_ascii=False, indent=1)
    # P2: Tool readiness matrix(评审 #56): 每工具契约完备度
    try:
        _rows = []
        for _n, _v in sorted(meta.items()):
            dims = {
                "schema": bool(_v.get("inputs")),
                "params": bool(_v.get("parameters")),
                "caps": bool(_v.get("capabilities")),
                "deps": bool(_v.get("dependency_manifest") or _v.get("dependencies")),
                "rels": bool(_v.get("relations")),
                "status": _v.get("status", "stable"),
            }
            score = sum(1 for k in ("schema", "params", "caps", "deps", "rels") if dims[k])
            _rows.append((_n, dims, score))
        full = sum(1 for _, d, s in _rows if s == 5)
        partial = sum(1 for _, d, s in _rows if 3 <= s < 5)
        lines = ["# Tool Readiness Matrix(自动生成, 勿手改)", "",
                 f"总览: {len(_rows)} 工具 | 契约完整(5/5): {full} | 部分(3-4): {partial} | 基础(<3): {len(_rows)-full-partial}", "",
                 "> 评审 #111 P1-2: 本表的 5/5 是 **metadata coverage**（Schema/Params/Caps/Deps/Rels 五个元数据维度），",
                 "> 与 readiness（FULL/PARTIAL/LEGACY, 判定维度 inputs/outputs/capabilities/parameters/stable）**不是同一套指标**",
                 "> ——FULL 工具在 metadata coverage 可能 3/5（缺 deps/rels 声明）, 勿混读。", "",
                 "| 工具 | Schema | Params | Caps | Deps | Rels | metadata coverage |",
                 "|---|---|---|---|---|---|---|"]
        for _n, _d, _s in _rows:
            def mark(b: bool) -> str:
                return "✅" if b else "—"
            lines.append(f"| `{_n}` | {mark(_d['schema'])} | {mark(_d['params'])} | {mark(_d['caps'])} | {mark(_d['deps'])} | {mark(_d['rels'])} | {_s}/5 |")
        open(_os.path.join(_out_root, "docs", "_generated", "tool-readiness.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    except Exception as _e2:
        print(f"⚠️ gen_metadata: tool-readiness.md 写盘失败: {_e2}", file=sys.stderr)  # 自审 gate P0-2: 静默 except 可见化

    # P1-9: contracts YAML 导出(评审 #56;CommandSpec → contracts/tools/*.yaml, 协议可读形式)
    try:
        import yaml as _y  # type: ignore[import-untyped]
        cdir = _os.path.join(_out_root, "contracts", "tools")
        _os.makedirs(cdir, exist_ok=True)
        for _sub in _os.listdir(cdir):
            _p = _os.path.join(cdir, _sub)
            if _p.endswith(".yaml"):
                _os.unlink(_p)
        from tbtools_cli.command_spec import build_command_specs as _bcs, to_metadata_entry as _tme
        for _n, _sp in _bcs().items():
            _e = _tme(_sp)
            if _e.get("inputs") or _e.get("parameters") or _e.get("capabilities"):
                _y.safe_dump(_e, open(_os.path.join(cdir, f"{_n}.yaml"), "w", encoding="utf-8"),
                             allow_unicode=True, sort_keys=False)
    except Exception as _e3:
        print(f"⚠️ gen_metadata: contracts YAML 导出失败: {_e3}", file=sys.stderr)  # 自审 gate P0-2: 静默 except 可见化
    manifest = {"schema_version": "1.0",
                "description": "tbtools-cli AI 机器接口层(Agent 程序化发现/理解/调用工具)",
                "files": ["tool-index.jsonl", "capability-index.json", "error-codes.json", "workflows.json", "relations.json", "tools/<group>/<cmd>.json"],
                "usage": {"discover": "tbtools search --input gff3 --output svg --json",
                          "describe": "tbtools tool-describe <cmd> --json",
                          "preflight": "tbtools tool-validate <cmd> <inputs...> --json",
                          "execute": "tbtools tool-run <args...> --json",
                          "provenance": "tbtools tool-provenance <output>"}}
    _json.dump(manifest, open(_os.path.join(ai_dir, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # 评审 #114 P1-4: renderer 自报 generated files——扫描 out_root 下本函数生成的
    # 全部区域(ai/ + contracts/tools/*.yaml + tool-readiness.md), Gate 自动覆盖
    # 未来新增文件(不再手工维护 surface 白名单)。
    # ⚠️ 路径基准: 记相对 **out_root**(非 ROOT)——check 对比时统一拼 ROOT 与 tmp
    for _root_area in (_os.path.join(_out_root, "ai"),
                       _os.path.join(_out_root, "contracts", "tools"),
                       _os.path.join(_out_root, "docs", "_generated", "tool-readiness.md")):
        if _os.path.isfile(_root_area):
            _written.add(_os.path.relpath(_root_area, _out_root))
        elif _os.path.isdir(_root_area):
            for _r, _ds, _fs in _os.walk(_root_area):
                for _fn in _fs:
                    _p = _os.path.join(_r, _fn)
                    if _fn.endswith((".bak", ".original.md")):
                        continue
                    _written.add(_os.path.relpath(_p, _out_root))
    print(f"✅ ai/ 生成: 工具索引 {len(meta)} + 能力 {len(cap_idx)} + 单工具 schema + 错误码")
    return _written


if __name__ == "__main__":
    sys.exit(main())