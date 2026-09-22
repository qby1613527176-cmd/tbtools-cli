# FAQ

- **Java 版本?** JRE 8+(推荐 11/17),`tbtools doctor` 自动检测
- **Windows?** 工具/RPC 全可用;绘图无 xvfb 部分受限(WSL2 推荐)
- **xvfb?** Linux 无头绘图必需:`sudo apt install xvfb`
- **管道?** 仅部分 tool 层;绘图命令需真实文件路径
- **大小写?** 小写 camelCase 为规范,旧大写为兼容别名
- **升级?** `git pull && pip install -e .`;JAR 用 `tbtools fetch-jar --yes`
