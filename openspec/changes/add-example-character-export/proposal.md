## Why

Root FEV `example-char`（Graph [`example-character-export-fev`](../../../pipelines/graphs/example/example-character-export-fev/pipeline.md)）证明：脚本生成的 Blender 角色可以由 Blender 5.1 headless 导出 FBX，并由 UE5.8 Editor Python 自动 import 为 native Skeleton / SkeletalMesh / MorphTarget / AnimSequence（Aggregate **FEASIBLE**，scope 为 `unit_cm`，2026-10-30）。实现目前只是 Graph 内的 experimental script。2026-10-30 [Promotion Recommendation](../../../docs/2026-10-30-example-character-blender-ue5/04-Promotion-Recommendation.md) 记为 `APPROVED`，把 exporter 落到示例业务项目 `repos/example-character-tools`。

## What Changes

- 新增 `example_character_tools/spec.py`：`CharacterSpec` / `BoneSpec` / `ActionSpec`、`validate()`、`mesh_data()`、`blender_to_ue_cm()`；不 import `bpy`。
- 新增 `example_character_tools/blender_export.py`：`build_character`、`export_fbx`、`export_character` 与 `inventory`；固定 FEV 确认的 unit 规则（`scale_length` 0.01、cm 数据）、`Armature` object 名称与 FBX 设置。
- 新增 add-on Operator `exchar.export_character`（`EXCHAR_OT_export_character`）与 File > Export 菜单项。
- 新增 headless CLI `cli/export_character.py`：exit 0 / 1 / 2 分别表示导出成功 / 导出失败 / 输入无效。
- 新增独立 ICD Graph [`example-character-export-acceptance`](../../../pipelines/graphs/example/example-character-export-acceptance/pipeline.md)。

## Capabilities

### New Capabilities

- `example-character-export`：把 `CharacterSpec` 构建为 Blender 角色并导出 UE5-ready FBX；UE5.8 自动 import 后 skeleton 干净（single root、bone scale 1）且结构与 Blender 一致。

### Modified Capabilities

*无*

## Impact

| 区域 | 影响 |
|------|------|
| `repos/example-character-tools/` | 新增（in-tree 示例项目） |
| `pipelines/graphs/example/example-character-export-acceptance/` | 新增 ICD Graph |
| 依赖 | 无新 pip 依赖；Blender 5.1、UE5.8 |
| 不包含 | rendering、retarget、Interchange import path（FEV `UNKNOWN`） |
