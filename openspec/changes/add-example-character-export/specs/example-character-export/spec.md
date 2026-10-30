## ADDED Requirements

### Requirement: Character spec validation before scene changes

系统 SHALL 在修改 Blender scene 之前校验 `CharacterSpec`：bone 名称唯一、ASCII、无空格；只有一个 root bone；每个 parent 在 child 之前声明；`half_width` 不小于 0；action bone 存在且 frames 有序。校验失败时系统 MUST 抛出 `ValueError`，headless CLI MUST 以 exit code 2 结束，且不写出 FBX。

#### Scenario: Two root bones are rejected

- **WHEN** CLI 收到包含两个 root bone 的 `--spec`
- **THEN** CLI 输出 `INVALID_INPUT` 并以 exit code 2 结束
- **AND** 输出目录中没有 FBX

### Requirement: UE-ready unit and naming rules

系统 SHALL 以 scene `scale_length` 0.01、cm 数据构建角色，armature object 名称 SHALL 为 `Armature`，FBX 导出 SHALL 使用 `FBX_EXPORT_SETTINGS`。

#### Scenario: Clean skeleton in UE5.8

- **WHEN** production CLI 导出的 FBX 在 UE5.8 中用 `FbxImportUI`（`convert_scene`、`import_morph_targets`、`import_animations`）import
- **THEN** skeleton 只有一个 root bone `root`，所有 bone 的 local scale 为 1（误差 1e-4）
- **AND** 所有 bone 的 component-space 位置等于 `blender_to_ue_cm(head_world)`（误差 0.01 cm）

### Requirement: Structure parity with the FEV canonical result

对 `default_character()`，production 输出 SHALL 与 FEV canonical inventory（blender-export Run `2026-10-30T154907`）一致：bone 名称与 parent、rest head（误差 1e-4 m）、vertex count、material slots、shape key 名称、action frame length。

#### Scenario: Default character matches FEV

- **WHEN** CLI 导出 `default_character()`
- **THEN** inventory 与 FEV canonical inventory 的上述字段一致
- **AND** UE5.8 import 得到 MorphTarget `belly_out`、`head_scale_up`，2 个 material slots，AnimSequence 长度与 action 一致
