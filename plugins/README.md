# plugins/ — TBtools 插件 CLI 化

来源：TBtools 官方插件商店（`http://43.155.73.187/configs/Plugin.store`，
由主 jar 内 `Plugin.PluginStore` 类解析）。`.plugin` 文件 = zip（MenuConfig.ini
+ Plugin_*.jar GUI 包装 + lib/ 依赖 + bin/ 捆绑二进制）。

本目录收录已 CLI 化的插件组件：

| 目录 | 来源插件 | 内容 | 许可 |
|:--|:--|:--|:--|
| `lib/Notung-2.9.1.5.jar` | P00651 Gene Gain and Lost Analysis | Notung 基因树-物种树 reconcile 引擎（duplication/loss 推断，CMU 开发，学术免费） | 见 Notung 原许可 |
| `src/*.plugin` | 插件商店 | 原始插件包存档（溯源用） | 各插件作者 |

CLI 入口：`tbtools tree notung <gene.nwk> -s <species.nwk> --reconcile [Notung 原生参数]`
