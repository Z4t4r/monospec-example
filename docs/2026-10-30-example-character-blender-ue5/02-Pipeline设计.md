# Example Character — Pipeline 设计

```yaml
doc_type: PIPELINE_DESIGN
lifecycle: ACTIVE
knowledge_state: CONFIRMED # 已 handoff，实际行为见 Graph
date: 2026-10-30
target_graph: pipelines/graphs/example/example-character-export-fev
approved_date: 2026-10-30
required_decision: "2026-10-30 用户：模板需要包含 Blender 与 UE5 的完整案例，不含来源资产与敏感内容"
implementation_authority: PIPELINE
```

## 路线

| Stage | 问题 | 输入 | 输出 | 下游 |
|---|---|---|---|---|
| S1 spec | 用什么角色可以不依赖外部资产，又覆盖 skeleton / skin / morph / material / animation？ | — | `character_spec.py` | S2 |
| S2 blender-export | headless build + FBX export 是否稳定？ | spec | `character.fbx`、`character_inventory.json` | S3 |
| S3 ue-import | UE5.8 自动 import 是否得到干净的 native asset？ | S2 的 FBX（sha256 固定） | `ue_result.json`、ref pose 比较 | Aggregate |
| S4 promotion | 结论是否足以进入业务模块？ | Aggregate | Promotion Recommendation | OpenSpec |
| S5 production + ICD | production exporter 是否保持 FEV 行为？ | OpenSpec change | ICD Run | Capability claim |

S2 与 S3 各为一个 Sub-FEV；S3 依赖 S2 的输出，所以按顺序执行。

## 结果去处

| 内容 | 位置 |
|---|---|
| intended design（本文件） | DOCS |
| contract、script、Run | [FEV Graph](../../pipelines/graphs/example/example-character-export-fev/pipeline.md) |
| Local / Aggregate Verdict | Sub-FEV Run 的 `summary.json`、[aggregate report](../../pipelines/graphs/example/example-character-export-fev/aggregate/report.md) |
| 解释与 Negative Findings | [03 Evidence 分析](03-FEV-Evidence分析.md) |
| production SHALL 与 tasks | [OpenSpec change](../../openspec/changes/add-example-character-export/proposal.md) |
| Capability Acceptance | [ICD Graph](../../pipelines/graphs/example/example-character-export-acceptance/pipeline.md) |

## 运行约束

- Blender：`--background --factory-startup`，不启动 UI。
- UE：每个 Run 新建 Worker project，`worker.json` 标记 owner，`fev_parallel` lease，`-NullRHI`，AIAGENT process owner 与 visible-window guard。
- 本机路径：`.local/environment.yaml`（gitignored）。

## 设计变更记录

| 日期 | 变更 | 原因（Run） |
|---|---|---|
| 2026-10-30 | `P2-action` 从“帧范围覆盖 1–30”改为“长度 30 帧” | blender-export `153748`：re-import 起始帧为 2，长度不变 |
| 2026-10-30 | 增加 `P2-bone-scale`；默认 variant 改为 `unit_cm` | ue-import `153931` / `154126`：m 单位导致 `root` scale 100 |
