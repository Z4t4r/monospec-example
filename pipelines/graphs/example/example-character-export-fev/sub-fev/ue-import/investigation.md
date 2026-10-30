# Sub-FEV example-char.ue-import

Parent：Root FEV `example-char`（[pipeline.md](../../pipeline.md)）。Runtime：UE5.8 fresh AIAGENT Worker，`-NullRHI`，`fev_parallel` lease（[`host_run/ue_worker.py`](../../../../../_shared/host_run/ue_worker.py)）。

## Question

UE5.8 Editor Python 自动 import 固定的 FBX 后，Skeleton / SkeletalMesh / MorphTarget / AnimSequence 的 bones、reference pose、bone scale、morph 名称、material slots 与动画长度是否与 Blender inventory 一致？

## Hypothesis

- H-axis：export 用 `-Z` forward / `Y` up，UE `convert_scene` 后 component position = Blender world head 的 `(x, -y, z) × 100`。名为 `Armature` 的 FBX node 被丢弃，`root` 仍是唯一 root bone。
- H-scale（第二轮加入）：Blender scene `scale_length` 0.01 且数据以 cm 写入时，export unit factor 为 1，UE 中所有 bone local scale 为 1。

## Experiment

[`scripts/ue_entry.py`](scripts/ue_entry.py) 在 Worker 中用 `AssetImportTask` + `FbxImportUI` import，`SkeletonModifier` 读取 bone transform，`AnimationLibrary` 读取动画。[`scripts/run_ue_import.py`](scripts/run_ue_import.py) 校验输入 sha256、启动 Worker、比较 inventory。

## Evidence 与 Local Verdict

| Run | 输入 Run（variant） | Local Verdict | 要点 |
|---|---|---|---|
| `2026-10-30T153931` | `153814`（default_m） | FEASIBLE（旧 contract） | 所有 check pass，但 readback 显示 `root` local scale = 100。旧 contract 没有检查 scale，因此该 Verdict 不能作为结论 |
| `2026-10-30T154126` | `153814`（default_m） | PARTIALLY_FEASIBLE | 新增 `P2-bone-scale` 后 fail：`root` scale 100。Negative Finding：m 数据 + `apply_unit_scale` 会把 unit factor 写进 root bone |
| `2026-10-30T154154` | `154153`（unit_cm） | FEASIBLE | 11/11 pass；ref pose 最大误差 6.7e-6 cm；bone scale 全为 1；AnimSequence 29 frame interval（30 keys） |
| `2026-10-30T154908` | `154907`（unit_cm） | FEASIBLE | 最终 script 重跑，结果与 `154154` 相同；canonical |

H-axis 与 H-scale 均得到支持（scope：本角色、UE 5.8.4、legacy FBX import path）。

## Limitations

`-NullRHI`，未检查 rendering / shading。MorphTarget delta、skin weight 与动画曲线数值没有逐项比较，只比较名称、数量与长度。`lod0_vertices` 为 408（render vertex 按 face normal 拆分），不与 Blender vertex count 直接比较。
