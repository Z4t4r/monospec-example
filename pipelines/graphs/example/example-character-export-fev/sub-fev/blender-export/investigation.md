# Sub-FEV example-char.blender-export

Parent：Root FEV `example-char`（[pipeline.md](../../pipeline.md)）。Runtime：Blender 5.1 `--background`。

## Question

Blender 5.1 headless 能否按 `character_spec` 生成角色，用固定设置导出一个 FBX，并在空 scene 中 re-import 后保持 bones、rest heads、vertex count、shape keys（名称与最大 delta）、material slots 和 action length？

## Hypothesis

默认 Blender FBX exporter 在 `contract.yaml` 的设置下保留以上数据。

## Experiment

[`scripts/blender_entry.py`](scripts/blender_entry.py) 在 Blender 内 build → `export_scene.fbx` → 清空 scene → `import_scene.fbx` → readback；[`scripts/run_blender_export.py`](scripts/run_blender_export.py) 在 host 侧与 spec 比较并写 Run bundle。`--variant` 选择 scene unit：`default_m`（`scale_length` 1）或 `unit_cm`（`scale_length` 0.01，数据以 cm 写入）。

## Evidence 与 Local Verdict

| Run | Variant | Local Verdict | 要点 |
|---|---|---|---|
| `2026-10-30T153748` | default_m | NOT_FEASIBLE | 只有 `P2-action` fail：re-import 后 action 范围变为 2–31，名称变为 `Armature\|Scene`。长度 30 帧不变；原规则检查范围过严，改为检查长度 |
| `2026-10-30T153814` | default_m | FEASIBLE | 8/8 pass；作为 ue-import 的对照输入 |
| `2026-10-30T154153` | unit_cm | FEASIBLE | 8/8 pass；rest head 误差 2.6e-7 m |
| `2026-10-30T154907` | unit_cm | FEASIBLE | 最终 script 重跑，结果与 `154153` 相同（inventory sha256 相同）；当前 canonical 输入 |

Negative Finding：Blender FBX importer 的 action 起始帧比 source 晚 1 帧，take 名称不保留。下游只应依赖 frame length。

## Limitations

只证明 Blender 内 round trip；UE 行为由 `example-char.ue-import` 回答。只测 rigid weight，不含 blended weight、custom normal 与 texture。
