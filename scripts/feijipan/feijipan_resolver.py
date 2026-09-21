#!/usr/bin/env python3
"""飞纪盘 64 插件批量解析器
流程: Plugin.store → 64 个 share.feijipan.com/s/XXX → /ws/share/list 递归遍历
     → 每个分享的文件树（.plugin 文件 + fileId + 大小）→ 索引 JSON + Markdown
加密: AES-128-ECB(key="dingHao-disk-app") uppercase-hex（已逐字节验证与前端 CryptoJS 一致）
"""
import subprocess, time, urllib.request, urllib.parse, json, sys

KEY_HEX = "dingHao-disk-app".encode().hex()
API = "https://api.feijipan.com"
UUID = "g-J6YrQ0AGL72Kd-NRROC"

def encrypt_hex(pt: str) -> str:
    p = subprocess.run(["openssl", "enc", "-aes-128-ecb", "-K", KEY_HEX],
                       input=pt.encode(), capture_output=True)
    return p.stdout.hex().upper()

def api_post(path: str, retries=4, **kw) -> dict:
    # ⚠️ 两个顺序/重试坑（09/21 实测）：
    # 1) 参数顺序敏感：devType/timestamp 块必须在前
    # 2) nginx 后端多机时钟不同步：随机命中偏差后端报「系统时间不正确」，
    #    必须用新 timestamp 重试（换后端即恢复）
    for attempt in range(retries + 1):
        head = {"devType": "6", "devModel": "Chrome", "uuid": UUID, "extra": "2",
                "timestamp": encrypt_hex(str(int(time.time() * 1000)))}
        head.update(kw)
        url = API + path + "?" + urllib.parse.urlencode(head)
        try:
            req = urllib.request.Request(url, method="POST")
            d = json.loads(urllib.request.urlopen(req, timeout=25).read())
            if d.get("code") == 200:
                return d
            if "时间不正确" in str(d.get("msg", "")) and attempt < retries:
                time.sleep(1.5)
                continue
            return d
        except Exception as e:
            if attempt == retries:
                return {"code": -1, "msg": str(e)}
            time.sleep(2)

def walk_share(share_id: str):
    """递归遍历分享，返回 (文件列表, 错误)"""
    files = []
    # 先拿根 folderId：recommend/list 或直接 share/list 不带 folderId
    d = api_post("/ws/share/list", shareId=share_id, offset=1, limit=110, referer="")
    if d.get("code") != 200:
        return [], f"root list 失败: {d.get('msg')}"
    root_items = d.get("list", [])
    # 根目录直接含文件的情况 + 需要 folderId 的情况
    # 从浏览器观察：share/list 需要 folderId（根 folderId 从页面上下文拿）
    # 但不带 folderId 也能返回根层（刚才 Rserver 验证：直接返回 3 文件夹）
    stack = [(it, "") for it in root_items]
    seen = 0
    while stack and seen < 500:
        item, prefix = stack.pop()
        seen += 1
        name = item.get("name") or item.get("fileName") or item.get("folderName") or "?"
        path = f"{prefix}/{name}" if prefix else name
        if item.get("fileId"):
            files.append({
                "path": path,
                "fileName": name,
                "fileId": item["fileId"],
                "fileSize": item.get("fileSize"),
                "userId": item.get("userId"),
                "updTime": item.get("updTime"),
            })
        else:
            # 文件夹：sortId 即 folderId
            fid = item.get("sortId") or item.get("folderId")
            if fid:
                sub = api_post("/ws/share/list", shareId=share_id, folderId=str(fid),
                               offset=1, limit=110, referer="")
                if sub.get("code") == 200:
                    for it2 in sub.get("list", []):
                        stack.append((it2, path))
    return files, None

def main():
    # 解析 Plugin.store 拿 64 个飞纪盘链接
    store = open("/tmp/Plugin.store", encoding="utf-8").read().splitlines()
    shares = []
    for line in store:
        if line.startswith("#") or not line.strip():
            continue
        cols = line.split("\t")
        if len(cols) >= 6 and "feijipan.com/s/" in cols[5]:
            sid = cols[5].split("/s/")[-1].strip()
            shares.append({"name": cols[0], "author": cols[2], "desc": cols[4][:60], "shareId": sid})
    print(f"飞纪盘分享总数: {len(shares)}")

    index = []
    for i, sh in enumerate(shares, 1):
        files, err = walk_share(sh["shareId"])
        plugins = [f for f in files if f["fileName"].endswith(".plugin")]
        entry = {**sh, "files": files, "plugins": plugins, "error": err}
        index.append(entry)
        status = f"{len(plugins)} plugin 文件" if plugins else ("⚠️ 无 .plugin" if not err else f"❌ {err}")
        print(f"[{i:2d}/{len(shares)}] {sh['name'][:40]:42s} {len(files):3d} 文件  {status}")
        time.sleep(0.4)  # 温和限速

    json.dump(index, open("/tmp/feijipan_index.json", "w"), ensure_ascii=False, indent=1)
    total_files = sum(len(e["files"]) for e in index)
    total_plugins = sum(len(e["plugins"]) for e in index)
    errors = [e for e in index if e["error"]]
    print(f"\n=== 汇总 ===")
    print(f"分享 {len(index)} / 文件总数 {total_files} / .plugin 文件 {total_plugins} / 失败 {len(errors)}")
    for e in errors:
        print(f"  ❌ {e['name']}: {e['error']}")

if __name__ == "__main__":
    main()
