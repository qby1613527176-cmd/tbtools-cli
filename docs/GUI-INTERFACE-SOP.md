# GUI 面板解析 → 逆向接口（TBtools CLI 化的权威接口发现法）

> 方法论文档（2026-09-20 确立，用户指定方向：**TBtools 主战场是 Windows；
> 找接口 = 解析 GUI，不是从引擎反猜**）。
> 适用：所有 TBtools 引擎/插件的 CLI 化攻坚，先读本文再动手。

## 为什么 GUI 是权威来源

TBtools 引擎的 `main()` 几乎全是硬编码作者机器路径的演示代码
（`C:\Users\CJ\Documents\...`），传参直接忽略；但 **GUI 面板类
（*GUIPanel.java）是引擎的"正确使用说明书"**——它写死了：

1. new 哪个引擎类
2. 调哪些 setter（字段名 = 真实参数名）
3. 按什么顺序调用 process()/build()/doXxx()
4. 参数怎么从界面控件读取（= 合法取值/格式）

反编译 GUIPanel → 照抄调用链 = 拿到官方正确接口，零猜测。

## 标准工作流（SOP）

### ① 找到 GUI 面板类

在 jar 里按功能关键词搜：

```bash
# 例：找"富集"相关的 GUI 面板
python3 -c "
import zipfile
z = zipfile.ZipFile('TBtools_JRE1.6.jar')
for n in z.namelist():
    if n.endswith('GUIPanel.class') and any(k in n.lower() for k in ('enrich','gsea','go')):
        print(n)"
```

### ② 反编译面板类（cfr.jar 在 tools/ 下）

```bash
unzip -o -q TBtools.jar "biocjava/GUIexcutors/GoAnanlysis/*.class" -d classes
java -jar tools/cfr.jar classes/.../GoEnrichMentGUIPanel.class \
     --extraclasspath classes --outputdir src
```

### ③ 读"按钮点击"回调（actionPerformed / run()）

GUI 逻辑都在 StartButton 的监听器里，形如：

```java
simpleHmmscan sh = new simpleHmmscan();
sh.setTargetPep(proteinFile);      // ← 真实参数名
sh.setPfamHmmA(pfamDbFile);
sh.setFinalOutFile(outFile);
sh.process();                       // ← 真实调用链
```

**这就是接口**。照抄到 Java 桥（bridges/*.java）。

### ④ 桥接（三种形态）

| 形态 | 适用 | 写法 |
|:--|:--|:--|
| setter+process 桥 | 面板直接调引擎 | 反射 `getMethod("setX", ...)` + `process()` |
| ArgsParser 直通 | 引擎 main 自带好用解析 | 直接 `java -cp jar 引擎 --key value` |
| 面板逻辑拆分 | 面板把引擎包进 GUI 弹窗（quickShow 等） | 只取面板里**引擎相关**代码段，绕开 GUI |

### ⑤ 排障铁律

- 引擎行为诡异 → `javap -p -cp jar 引擎类` 看字段名（javap 是权威）
- 参数名不确定 → 面板源码里 setter 就是真名，别猜
- 位置参数 vs `--key value` → 看面板代码怎么传；ArgsParser 系一律空格分隔
- 面板里嵌了外部二进制（hmmsearch/kallisto/diamond）→ 找它调用的裸命令名

## 已用此法的实战案例

| 功能 | 面板 → 引擎 | 关键发现 |
|:--|:--|:--|
| HMM Search | SimpleHMMsearchGUIPanel → simpleHmmscan | GUI 的"HMM Search"就是 simpleHmmscan，CLI 已有，仅缺别名（G1） |
| GO 富集 | GoEnrichMentGUIPanel → GOTermEnrichment | prepareForEnrichMent + AutoEnrichMent 两段式 |
| 一步法建树 | OneStepBuildATreeGUIPanel → OneStepMLTree | 2.475/2.535 jar 均无 Phylogenetics.OneStepTree（注册名错） |
| kallisto | KallistoWrapper（插件面板） | Linux 分支拼接 bug → 绕开直调二进制 |
| qdot | QuickGenomeDotPlot.process() | 尾部 quickShow GUI 弹窗 headless 崩 → 直驱 dotdotdot 引擎 |

## Windows 平台检查清单（GUI 之外的第二主线）

CLI 化产物必须过这份 Windows 审计：

- [ ] classpath 用 `cp()`（Windows `;`），不硬编码 `:`
- [ ] 二进制：插件自带 `.exe`（PE32+）提取进 `plugins/lib/bin/`；Linux ELF 并存
- [ ] `/dev/stdout` → `stdout_path()`（Windows 用 CON）
- [ ] bash 兜底：Windows 无 Git Bash 时报清晰错误
- [ ] xvfb：`run_plot` 已 which 检测，Windows 自动直跑
- [ ] 路径：`/mnt/d` 风格仅在 WSL 有效；Windows 用 `C:/` + 分号 classpath
