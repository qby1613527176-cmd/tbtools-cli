# 快速开始

```bash
# 1. 配置 JAR(三选一)
tbtools doctor                 # 环境自检,给指引
tbtools setup --auto           # 自动搜索本机 TBtools
tbtools fetch-jar --yes        # 自动下载官方包提取 JAR

# 2. 出第一张图
tbtools expr volcano examples/data/deg.txt volcano.svg --pval-cutoff 0.05

# 3. 探索
tbtools list plots             # 218 个绘图命令
tbtools search volcano         # 模糊搜索
tbtools help volcano           # 命令详情(含坑位提示)
tbtools new                    # 交互式向导
```

> 最小示例数据:`git clone` 仓库后 `examples/data/`。
> 退出码: 0 成功 / 1 参数数据错 / 2 文件缺失或未知命令 / 3 格式不匹配 / 4 内存不足。
