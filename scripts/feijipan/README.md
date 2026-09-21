# 飞纪盘 64 插件解析器（2026-09-21 攻克）

TBtools PluginStore（`http://43.155.73.187/configs/Plugin.store`，127 行）
= 52 直链 + 64 飞纪盘 + 3 奶牛快传。本目录是 64 个飞纪盘分享的完整解析成果。

## 文件

- `Plugin.store` — 官方插件目录快照（2026-09-21）
- `feijipan_resolver.py` — 解析器（枚举 + 下载 URL 生成）
- `feijipan_index.json` — 64 分享完整文件树索引（79 个 .plugin 文件，含 fileId/大小/路径）

## 技术要点（踩坑记录，复用必看）

1. **分享 API**：`POST https://api.feijipan.com/ws/share/list`，参数
   `devType=6&devModel=Chrome&uuid=<uuid>&extra=2&timestamp=<enc>&shareId=<id>&folderId=<id>&offset=1&limit=110`
2. **timestamp 加密**：AES-128-ECB(key=`dingHao-disk-app`, Pkcs7) → 大写 hex，
   明文为毫秒时间戳字符串。前端 CryptoJS 与 openssl `-aes-128-ecb` 逐字节一致。
   （密钥硬编码于 app.js 模块 6686：`atob("ZGluZ0hhby1kaXNrLWFwcA==")`）
3. **`limit` 必须 ≤110**：limit=200 报「系统时间不正确」（误导性错误消息，实为参数校验失败）
4. **参数顺序敏感**：devType/timestamp 块必须放查询串前部
5. **文件夹递归**：根调用（不带 folderId）返回顶层条目；文件夹用 `sortId` 作为 folderId 继续调
6. **下载 URL**（确定性生成，与页面按钮逐字节一致）：
   ```
   GET /ws/file/redirect?downloadId=<AES(fileId+"|")>&enable=1&devType=6&uuid=<uuid>&timestamp=<AES(ms)>&auth=***&shareId=<id>
   ```
   ⚠️ **仅真实浏览器导航（页面按钮/地址栏）放行 302**；curl/curl_cffi/fetch
   一律「参数有误」（服务端区分 navigation vs 合成请求，TLS/Sec-Fetch 指纹均无法绕过）。
   实际批量下载走浏览器按钮点击（已验证 3 次成功）；生成的 URL 给用户浏览器打开即可。
7. **统计**：64 分享 = 79 文件（13 个多平台包：windows/macos_intel/macos_arm），
   .plugin 总 ~7GB（单个 134KB~698MB）

## 用法

```bash
python3 feijipan_resolver.py   # 重扫 64 分享（~3min，温和限速 0.4s/分享）
```
