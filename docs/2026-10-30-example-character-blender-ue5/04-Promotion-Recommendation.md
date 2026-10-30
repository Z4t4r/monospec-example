# Example Character — Promotion Recommendation

```yaml
doc_type: DECISION
lifecycle: ACTIVE
knowledge_state: CONFIRMED
date: 2026-10-30
decision_state: APPROVED
authority: Human Promotion Decision；normative SHALL 由 OpenSpec change 持有
```

## Recommendation

把 FEV 已验证的 exporter 行为写成 `repos/example-character-tools` 的业务模块，并以独立 ICD Graph 验收。

| 项 | 建议 | 依据 |
|---|---|---|
| 范围 | `CharacterSpec`（纯 Python）+ Blender `build_character` / `export_fbx` + CLI | FEV Root FEASIBLE |
| 必须保留 | `scale_length` 0.01 + cm 数据；`Armature` object 名称；contract 中的 `fbx_export` 设置 | Negative Finding：root scale 100 |
| 改写而非复用 | 不 import FEV script；spec 与 builder 分层，便于 unit test | Pipeline policy：Graph 不拥有业务代码 |
| 验收 | ICD Graph 运行 production CLI，再在 UE5.8 Worker 中 import，与 FEV canonical inventory 比较 | ICD L1–L3 |
| 不包含 | rendering、retarget、Interchange path | FEV Unknown |

## Decision

2026-10-30，用户在本仓的请求中要求模板提供“一个完整的包含 UE5 和 Blender 的案例，且不包含当前项目的资产和敏感内容”，并授权对 `monospec-example` 做任意修改。完整案例包含 production 实现与 ICD，因此本 Recommendation 记为 `APPROVED`。范围只限上表。

后续：[OpenSpec change `add-example-character-export`](../../openspec/changes/add-example-character-export/proposal.md)。
