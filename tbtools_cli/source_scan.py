"""source_scan.py — AST 源码扫描(arch N5 中期: 正则脆弱性簇根因消灭).

背景(评审 #115 arch N5): command_spec 与 gen_metadata 两侧用正则扫描 cli.py /
auto_commands.py 提取命令名+docstring, 脆弱点:
  1. 装饰器正则强制 docstring(无 docstring 的新命令 → 进 metadata 不进 specs → 漂移)
  2. `@\\w+_group.command` vs 顶层 `@cli.command` 两侧口径不同 → 单侧漂移
  3. 参数段 `[^)]*` 遇默认值含 `)` 断链, 后续命令 doc 错配
  4. 非贪婪 `[\s\S]*?` 无 docstring 时把下一条命令的 docstring 错配给前一条
  5. `[^"]` docstring 内双引号提前截断(如 tableMerge --inFileArr "f1,f2")

AST 方案: ast.parse 一次, FunctionDef 的 decorator_list + 模块级 add_command Call
全拿到——decorator 就是 decorator, docstring 就是 docstring, 不存在错配/断链。
doc 用 ast.get_docstring(cleandoc 语义: 去公共缩进 + Python 转义)——比正则文本
更干净且内容等价(298=298 由 test_specs_match_metadata 字段级比对守卫)。

生成端(gen_metadata)与模型端(command_spec)共用本模块——禁止两侧复制扫描逻辑。
"""

from __future__ import annotations

import ast
from typing import Dict, Optional


def ast_scan_commands(cli_src: str, ac_src: str) -> Dict[str, Dict]:
    """AST 扫描 cli.py + auto_commands.py → {name: {group, doc, src, fn}}.

    - group: 装饰器前缀推导(expr_group → "expr"); 顶层 @cli.command → None
      (消费侧按 KNOWN_TOP_MANUAL 过滤); add_command → 同前缀推导; auto impl → None
      (消费侧按 CATEGORY_MAP 推断)。
    - doc: cleandoc 语义, 截 300(与旧正则 `{0,300}` 对齐)。
    - src: "cli_manual"(装饰器/add_command) | "auto_manual"(_xxx_impl)。
    - fn: 函数名(add_command 时为首参数函数名, 供 help 借用)。
    """
    out: Dict[str, Dict] = {}

    def _cmd_name_from_call(_call: ast.Call) -> Optional[str]:
        _name = None
        if _call.args and isinstance(_call.args[0], ast.Constant) and isinstance(_call.args[0].value, str):
            _name = _call.args[0].value
        for _kw in _call.keywords:
            if _kw.arg == "name" and isinstance(_kw.value, ast.Constant) and isinstance(_kw.value.value, str):
                _name = _kw.value.value
        return _name

    # ---- cli.py ----
    try:
        tree = ast.parse(cli_src)
    except SyntaxError as _e:
        import warnings as _w
        _w.warn(f"cli.py AST 解析失败(源码语法错误), 命令扫描不可用: {_e}", SyntaxWarning, stacklevel=2)
        return out
    for node in ast.walk(tree):
        # 模块级 add_command 注册调用(不在函数装饰器上): seq_group.add_command(fn, name="alias")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and isinstance(node.func.value, ast.Name) \
                and node.func.value.id.endswith("_group") and node.func.attr == "add_command":
            _n = _cmd_name_from_call(node)
            if _n:
                _fn2 = node.args[0].id if node.args and isinstance(node.args[0], ast.Name) else ""
                # group=None: 消费侧按 CATEGORY_MAP 推断(旧行为)——add_command 无装饰器
                # 前缀可推, 与前缀推断在 seqlogo 等命令上产生差异(快照校验实测抓到)
                out.setdefault(_n, {"group": None, "doc": "",
                                    "src": "cli_manual", "fn": _fn2})
        if not isinstance(node, ast.FunctionDef):
            continue
        _doc = (ast.get_docstring(node) or "").strip()[:300]
        for _dec in node.decorator_list:
            if not isinstance(_dec, ast.Call):
                continue
            _f = _dec.func
            if not isinstance(_f, ast.Attribute) or not isinstance(_f.value, ast.Name):
                continue
            _grp, _meth = _f.value.id, _f.attr
            if _meth == "command" and _grp.endswith("_group"):
                _n = _cmd_name_from_call(_dec)
                if _n:
                    out.setdefault(_n, {"group": _grp[:-6], "doc": _doc,
                                        "src": "cli_manual", "fn": node.name})
            elif _meth == "command" and _grp == "cli":
                _n = _cmd_name_from_call(_dec)
                if _n:
                    # 顶层管理命令: group=None, 消费侧 KNOWN_TOP_MANUAL 过滤
                    out.setdefault(_n, {"group": None, "doc": _doc,
                                        "src": "cli_manual", "fn": node.name})

    # ---- auto_commands.py 手写 impl ----
    try:
        tree2 = ast.parse(ac_src)
    except SyntaxError as _e2:
        import warnings as _w2
        _w2.warn(f"auto_commands.py AST 解析失败: {_e2}", SyntaxWarning, stacklevel=2)
        return out
    for node in ast.walk(tree2):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("_") and node.name.endswith("_impl"):
            _n = node.name[1:-5]
            _doc = (ast.get_docstring(node) or "").strip()[:300]
            out.setdefault(_n, {"group": None, "doc": _doc,
                                "src": "auto_manual", "fn": node.name})
    return out
