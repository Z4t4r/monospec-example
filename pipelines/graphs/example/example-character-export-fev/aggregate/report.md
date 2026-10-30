# Aggregate report — Root FEV example-char

Root Question：见 [`config.yaml`](../config.yaml) `fev.question`。Graph：`example-character-export-fev`。日期：2026-10-30。

## Aggregate Verdict

**FEASIBLE**（scope：`unit_cm` variant、Blender 5.1.2、UE 5.8.4 CL58902052、legacy FBX import path、本示例的 rigid 角色）。

## Local Verdicts used

| Sub-FEV | Run | Local Verdict | 用作 |
|---|---|---|---|
| `example-char.blender-export` | `2026-10-30T154907`（unit_cm） | FEASIBLE | Blender build / export / re-import 证据；inventory sha256 `46900d52…`，FBX sha256 `5b332446…` |
| `example-char.ue-import` | `2026-10-30T154908`（输入 `154907`） | FEASIBLE | UE import 后 bones、ref pose、bone scale、morph、material、animation 一致 |

`154153` / `154154` 是相同 variant 的前一轮 Run，结果相同；`154907` / `154908` 用最终 script 重跑（之后只改了类型注解），作为 canonical。

Durable canonical：[`canonical/character_inventory.json`](../canonical/character_inventory.json) 是 `154907` 的 `evidence/character_inventory.json` 副本（sha256 `46900d52…`）。`runs/` 不进 Git，ICD Graph 从这个 tracked 副本读取参考数据。

## Negative Findings

| Run | Finding | 对路线的影响 |
|---|---|---|
| blender-export `2026-10-30T153748` | re-import 后 action 起始帧晚 1 帧，take 名称不保留 | 下游只依赖 frame length，不依赖起始帧或 action 名称 |
| ue-import `2026-10-30T153931` / `154126`（输入 `default_m`） | scene 以 m 为单位时，UE 把 unit factor 100 写入 `root` bone scale | production exporter 必须使用 `scale_length` 0.01 + cm 数据；contract 增加 `P2-bone-scale` |

## Interpretation

Local Verdict 不直接传播：Root 结论成立，是因为两个 Sub-FEV 都在同一 variant 上 FEASIBLE，且 ue-import 的输入经 sha256 绑定到 blender-export 的 Run。`default_m` 路线证明了“默认设置看似通过但 skeleton 不干净”，因此 Root 只对 `unit_cm` 成立。

## Implementation guidance

- 使用 `contract.yaml` 的 `fbx_export` 设置、`Armature` object 名称与 `scale_length` 0.01。
- Production 实现另写到业务模块，不 import 本 Graph 的 script；production 输出须由独立 ICD Graph 重新验证 bones、ref pose、bone scale、morph 与 animation。

## Limitations / Unknown

未检查 rendering、MorphTarget delta 数值、skin weight 与动画曲线数值；Interchange import path 与其他 engine build 为 `UNKNOWN`。

## Reproduction

见 [pipeline.md](../pipeline.md#invoke)。
