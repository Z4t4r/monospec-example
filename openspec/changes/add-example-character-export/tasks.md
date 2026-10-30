## 1. Spec（纯 Python）

- [x] 1.1 `spec.py`：`CharacterSpec` / `BoneSpec` / `ActionSpec`、`default_character()`、`validate()`
- [x] 1.2 `mesh_data()`：box mesh、rigid vertex groups、`head_scale_up` / `belly_out` shape keys
- [x] 1.3 `tests/test_spec.py`：结构、shape key delta、invalid spec、UE mapping

## 2. Blender export

- [x] 2.1 `blender_export.py`：`build_character`（unit 规则、Edit Mode 只用于 edit bones 并恢复）、`export_fbx`、`inventory`、`export_character`
- [x] 2.2 `operators.py`：`EXCHAR_OT_export_character`、File > Export 菜单、`register()` / `unregister()` 成对
- [x] 2.3 `cli/export_character.py`：`--output-dir`、`--spec`，exit code 0 / 1 / 2

## 3. Acceptance

- [x] 3.1 ICD Graph `example-character-export-acceptance`：L1 production CLI、L2 Blender 输出与 FEV canonical parity、L3 UE5.8 Worker import parity、invalid input
- [x] 3.2 执行 ICD Run 并在 Graph 与 DOCS 中记录 Run identity
