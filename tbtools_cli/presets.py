"""出版级预设模板 — 期刊风格一键应用"""
import os, json

# 预设定义
PRESETS = {
    # ── 期刊预设 ──
    "nature": {
        "desc": "Nature: 单栏 89mm, 双栏 183mm, 8pt, Arial, 300dpi",
        "width": 89, "height": 89, "dpi": 300,
        "font": "Arial", "font_size": 8,
        "palette": "nature",
    },
    "cell": {
        "desc": "Cell: 单栏 85mm, 双栏 170mm, 7pt, Arial, 300dpi",
        "width": 85, "height": 85, "dpi": 300,
        "font": "Arial", "font_size": 7,
        "palette": "cell",
    },
    "plant_journal": {
        "desc": "Plant Journal: 单栏 80mm, 双栏 170mm, 8pt, Helvetica, 300dpi",
        "width": 80, "height": 80, "dpi": 300,
        "font": "Helvetica", "font_size": 8,
        "palette": "viridis",
    },
    "new_phytologist": {
        "desc": "New Phytologist: 单栏 80mm, 双栏 170mm, 7pt, Arial, 300dpi",
        "width": 80, "height": 80, "dpi": 300,
        "font": "Arial", "font_size": 7,
        "palette": "viridis",
    },
    "wide": {
        "desc": "宽幅: 183mm 双栏, 8pt, Arial, 300dpi",
        "width": 183, "height": 120, "dpi": 300,
        "font": "Arial", "font_size": 8,
        "palette": "viridis",
    },
    "poster": {
        "desc": "海报: 大尺寸 400×300mm, 12pt, Arial, 150dpi",
        "width": 400, "height": 300, "dpi": 150,
        "font": "Arial", "font_size": 12,
        "palette": "set2",
    },
    # ── 色板预设 ──
    "gras": {
        "desc": "GRAS 项目: 17 亚家族定色, viridis 底色",
        "palette": "gras17",
    },
}

# 色板定义
PALETTES = {
    "nature": ["#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F",
                "#EDC948", "#B07AA1", "#FF9DA7", "#9C755F", "#BAB0AC"],
    "cell": ["#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD",
             "#8C564B", "#E377C2", "#7F7F7F", "#BCBD22", "#17BECF"],
    "viridis": "viridis",  # 引擎内置
    "set2": "set2",
    "gras17": ["#E64B35", "#4DBBD5", "#00A087", "#3C5488", "#F39B7F",
               "#8491B4", "#91D1C2", "#DC0000", "#7E6148", "#B09C85",
               "#FF9DA7", "#9C755F", "#BAB0AC", "#76B7B2", "#59A14F",
               "#EDC948", "#B07AA1"],
}

def get_preset(name):
    """获取预设配置，返回 dict 或 None"""
    return PRESETS.get(name)

def list_presets():
    """列出所有预设"""
    return [(k, v["desc"]) for k, v in PRESETS.items()]

def apply_preset(name, width=None, height=None):
    """应用预设，返回参数 dict。用户显式指定的 width/height 覆盖预设值"""
    p = get_preset(name)
    if not p:
        return {}
    result = {}
    if width is None and "width" in p:
        result["width"] = p["width"]
    if height is None and "height" in p:
        result["height"] = p["height"]
    if "dpi" in p:
        result["dpi"] = p["dpi"]
    if "font" in p:
        result["font"] = p["font"]
    if "font_size" in p:
        result["font_size"] = p["font_size"]
    if "palette" in p:
        result["palette"] = p["palette"]
    return result

def load_custom_preset(path):
    """从 JSON 文件加载自定义预设"""
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        data = json.load(f)
    PRESETS[data.get("name", "custom")] = data
    return data
