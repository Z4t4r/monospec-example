# python-dialect

Trait：编写或修改本仓 / `repos/<project>` 的 Python 之前，**先选方言，再写文件**。

本文件是 Python 落点、运行时与错误通道的**唯一权威**。  
**不是** PEP 8 摘录，**不是** Python mixin / Enthought Traits，**不是** ruff 配置。  
通用缩进、`snake_case`、Google docstring 以训练默认值即可；此处只写本仓已经踩过、且通用经验会写错的边界。

加载时机：新建或改写 `.py`（含 Graph `scripts/`、`cook_runtime`、Blender add-on、隔离 cook）之前 **MUST** 读完全文。  
本 trait **只**留在 monospec `traits/`。**MUST NOT** 同步到 `repos/*/traits/` 或子仓业务树。

## 它约束什么

| 方言 | 允许落点 | 运行时 | 禁止 |
|------|----------|--------|------|
| host-evidence | `pipelines/_shared/cook_runtime/` | 宿主 CPython | `import bpy`；Node / TS 运行时 |
| host-transform | 对应 Graph 的 `scripts/`，并标 experimental | 宿主 CPython（不进 Blender） | `import bpy`；把本机绝对路径当唯一输入 |
| blender-isolated | `repos/<project>/pipelines/`，或该 Graph 的 `scripts/` | Blender 5.1 内置解释器 | re-export 成业务公共 API；声称已产品化 |
| blender-addon | `repos/<project>/<addon>/`，且仅在 OpenSpec **明确参考**对应 Graph 并落地之后 | 同上 | 新 pip 依赖；在 `register()` 顶层硬导入可选插件 |
| foreign | UE Editor Python、上游仓、`.agents/skills/`、`_bmad/` | 各自 | 套用本 trait 的 Blender 命名去重排 |
| repository-policy | `.github/scripts/` | 宿主 CPython | `bpy`、业务实现、资产转换与写入 project artifacts |

`scripts/`（仓库根）**只**放 deploy。Python 变换、splice、分析、一次性实验 **MUST NOT** 再落入该目录。

## 先分流（NON-NEGOTIABLE）

写文件之前 **MUST** 在回复或文件模块 docstring 里点明方言。缺方言 → **停止**，不要猜成「通用 Blender 脚本」。

1. 文件会在 Blender 里执行（`bpy`）→ `blender-isolated` 或 `blender-addon`。未走 OpenSpec 产品化 → **只能** isolated。
2. 文件只写证据包 / 读跑目录 → `host-evidence`。**MUST NOT** 为此引入 `bpy`。
3. 文件解析或改写磁盘资产、且不需要 Blender → `host-transform`，落在**该 Graph** 的 `scripts/`。
4. 文件属于上游仓、UE Editor、BMAD → `foreign`。读可以；**MUST NOT** 按本 trait 重排其风格。
5. 文件只读检查 repository policy、metadata 或 links，并由 CI 调用 → `repository-policy`，只能落在 `.github/scripts/`。

跨方言 **MUST NOT** import：

- `cook_runtime` **MUST NOT** `import bpy`。
- Blender 内脚本 **MUST NOT** 依赖宿主 venv / 未随 Blender 分发的包。
- 隔离脚本 **MUST NOT** 被业务 `__init__.py` re-export 成公共 API。

## 版本地板

地板是 `bl_info["blender"] == (5, 1, 0)` 的**内置解释器**，不是本机更新的 CPython。

- 新代码 **MUST** `from __future__ import annotations`。
- 新注解用 `X | None`，不用新引入的 `Optional[X]`。
- **MUST NOT** 为了统一注解，把既有 `Optional` 整文件改写。
- **MUST NOT** 使用该解释器尚不支持的语法。宿主侧 `cook_runtime` 与 Graph `scripts/` 同样不得超过这个地板。

## blender-bpy

addon 与隔离 cook **共用**本节。隔离脚本额外遵守「隔离」小节。

### API

- 变更场景数据 **MUST** 走 Data API（`bpy.data`、bone / vertex group / constraint、engine-native data path）。
- `bpy.ops` **仅**允许：没有 Data API 的 import / export、Mode 切换、以及产品 Invoke 本身就是 Operator。
- **MUST NOT** 把 `bpy.ops` + `print` + 吞掉 `Exception` 当作模板。那是已废止的反例，不是风格。

### 命名与注册

沿用所在插件已有前缀。由目标插件定义；以下是命名结构：

| 种类 | 形式 |
|------|------|
| Operator / Panel / Menu | `<PREFIX>_OT_*` / `<PREFIX>_PT_*` / `<PREFIX>_MT_*` |
| `bl_idname` | `<prefix>.*` |
| 隔离 cook 入口 | `run_<graph>(..., report_dir=)` |

- **MUST NOT** 为同一插件另起前缀。
- 标识符、函数名、属性名保持英文。`bl_label` 可沿用插件既有中文；**MUST NOT** 把 docs 禁止单独使用的 UI 译名（如「物体模式」）写进新文案。专用名词规则见 [`../docs/AGENTS.md`](../docs/AGENTS.md)。
- `register()` / `unregister()` **MUST** 成对。可选依赖经目标插件 compat 层检测，缺失时降级。
- **MUST NOT** 在模块顶层或 `register()` 里硬 import 可选依赖 导致整个插件启用失败。

### 错误与副作用

| 通道 | 规则 |
|------|------|
| Operator | `self.report` + 返回 `{"CANCELLED"}` / `{"FINISHED"}`。**MUST NOT** 用 `print` 当错误通道 |
| 缺对象 / 类型不对 | 具体失败原因进 report；需要中止 cook 时抛 `ValueError` / `TypeError`，不要裸 `except Exception` |
| Mode | 用完恢复进入前的 Mode。**MUST NOT** 把用户留在 Edit Mode |
| `.blend` | **MUST NOT** 默认保存。仅当对应 `pipeline.md` 的 Gate 写明保存时才保存 |
| in-place | 会改现有对象的 cook **MUST** 在 `pipeline.md` 声明 `Cook: in-place` |

### 隔离（blender-isolated）

- 新 experimental cook **MUST** 落在 `repos/<project>/pipelines/` 或该 Graph 的 `scripts/`。
- **MUST NOT** 再把新的 `run_*` 挂进 `<addon>/` 业务模块。隔离 cook **MUST NOT** 挂回业务 core；已有历史债务不是模板。
- 成功条件是结构化 checks + `report_dir` 证据，不是面板状态文案。
- 文中与模块 docstring **MUST** 标明 `experimental` / `isolated`。未走 OpenSpec **MUST NOT** 声称已是插件正式功能。
- 隔离与产品化路径以 [`pipelines-trait.md`](./pipelines-trait.md) 为准；本 trait 不重复 Graph 写法。

## host-python

`host-evidence` 与 `host-transform` 共用本节。

- 证据包 **MUST** 用 `pipelines/_shared/cook_runtime`：`summary.json` / `report.md`；仅 Graph 显式要求最终用户验收时增加 `acceptance.md`。缺证写 `source: missing`（及 `count: 0`），**禁止**静默跳过。
- FEV 使用 `write_run_bundle(..., fev={...})` 提供 question、outcome、observations、interpretation、verdict、limitations、guidance、evidence、reproduction；不生成 acceptance / 人工 pass Footer。判定条件留在 experiment / contract。
- P3 **MUST NOT** 由 Agent 标 pass。业务 Graph 需要用户验收时显式传 `human_acceptance=True`（或既有 `acceptance_template`）；仅该模式显示用户验收 Footer。
- 路径用 `pathlib`。读写文本 **MUST** `encoding="utf-8"`。
- 输入由参数或 Graph `config.yaml` 传入。**MUST NOT** 把 `<machine-local-asset-root>` 一类本机绝对路径写成唯一合同。
- 失败抛具体异常（`ValueError`、`FileNotFoundError`、`OSError`）。**MUST NOT** `except Exception` 后 `print` 并返回假成功。
- **MUST NOT** 为 pipelines 引入 Node / TypeScript / pnpm 运行时。

`host-transform` 若要留存，放在**该 Graph** 的 `scripts/`，模块 docstring 标明 experimental。不要放进 `pipelines/_shared/cook_runtime/`（那里只放证据 helper），也不要放进仓库根 `scripts/`。

## repository-policy

- validator MUST 保持 read-only；不得修复、移动或生成被检查的 project artifact。
- 只使用 Python standard library；不得为 policy check 引入新的 runtime dependency。
- path handling 使用 `pathlib`，文本使用 UTF-8，validation failure 返回 non-zero exit code。
- historical debt MAY 使用显式 baseline，但新增 drift MUST 失败；baseline 不得把新错误静默加入。
- validator 不判断 semantic truth、Human Decision 或 Trait maturity，只检查确定性 contract。

## 明确不覆盖

| 范围 | 处理 |
|------|------|
| `.agents/skills/**`、`_bmad/` | foreign；不要重排 |
| `repos/<upstream>` 等上游 | 只读；他们的风格优先 |
| `repos-meta/<project>/AGENTS.md` 的领域规则 | 仍以该文件为准（目标项目的 domain / Data path）。编码边界以本 trait 为准 |
| `standard_words.yaml` | 用语表，不是运行时契约。见 [`standard-words-trait.md`](./standard-words-trait.md) |
| ruff / black / `pyproject.toml` | 本 trait 不引入。没有与 Blender 内置解释器对齐的 lint 配置之前，不要为了「标准化」加格式化工具 |

## 与其它文档的关系

冲突时 **以本文件更严者为准**。

| 文档 | 关系 |
|------|------|
| [`openspec/AGENTS.md`](../openspec/AGENTS.md) Python Style | **指针**。其中旧的 `bpy.ops` + `print` 示例已废止，**MUST NOT** 再当模板 |
| [`openspec/project.md`](../openspec/project.md) Coding Style | **指针**。禁止把「直接改 scene 是 Bad、`bpy.ops` 是 Good」当规则 |
| [`repos-meta/AGENTS.md`](../repos-meta/AGENTS.md) | 具体项目领域留在其 metadata；Code Style 指向本 trait |
| [`pipelines/AGENTS.md`](../pipelines/AGENTS.md) | Graph 选型与证据包结构；写 `.py` 时仍须本 trait |
| [`scripts/AGENTS.md`](../scripts/AGENTS.md) | 根目录只允许 deploy；与本 trait 的落点表一致 |

## 反模式

| 反模式 | 正确做法 |
|--------|----------|
| 未选方言就生成「带 `bpy` 的工具脚本」 | 先归入上表一行 |
| `except Exception as e: print(...)` 后返回 `None` / `False` | Operator 用 `self.report`；host 抛具体异常 |
| 变更骨 / VG / constraint 却调用 `bpy.ops` | Data API |
| 新 cook 函数写进 `<addon>/*.py` 并标 experimental | `repos/<project>/pipelines/` 或 Graph `scripts/` |
| splice / 解析脚本放进仓库根 `scripts/` | Graph `scripts/`（host-transform） |
| `cook_runtime` 里 `import bpy` | 禁止；证据 helper 保持无 Blender |
| 把本机资产路径写死为唯一输入 | 参数或 `config.yaml` |
| 缺证据就跳过 collector | `source: missing` |
| 用本 trait 重排 upstream / BMAD 脚本 | foreign，不动风格 |
| 把本文件复制进 `repos/<project>/traits/` | 只留 monospec `traits/`，子仓用指针 |

## Agent 检查清单

- [ ] 本次 `.py` 是否已点明方言？落点是否在该方言允许的目录？
- [ ] 是否把非 deploy 的 Python 写进了仓库根 `scripts/`？
- [ ] 是否在未走 OpenSpec 的情况下改了 `<addon>/` 的公共 API？
- [ ] blender 路径是否用 Data API（ops 是否落在允许的三种例外里）？
- [ ] 错误是否走了该方言的通道，而不是 `print` + 吞异常？
- [ ] host 证据是否经 `cook_runtime`，缺证是否写了 `source: missing`？
- [ ] 是否引入了 Blender 内置解释器没有的依赖或更新语法？
- [ ] 是否把 trait 同步进了子仓，或重排了 foreign 代码？
