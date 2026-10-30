## Context

FEV Graph 的 `scripts/character_spec.py` 与 `blender_entry.py` 证明了行为，但它们是 experimental script，并且混合了 build、readback 与 Evidence 写入。Production 需要分层，便于 host 测试与 add-on 复用。

## Decisions

1. **分层**：`spec.py`（纯 Python，host 可测）→ `blender_export.py`（bpy）→ `operators.py` / `cli/`（入口）。不 import FEV script。
2. **Unit 规则**：`SCALE_LENGTH = 0.01`，数据以 cm 写入。依据：FEV ue-import Run `2026-10-30T154126`（m 单位 → `root` scale 100）与 `2026-10-30T154908`（cm → scale 1）。
3. **FBX 设置**：沿用 FEV contract 的 `fbx_export`，集中在 `FBX_EXPORT_SETTINGS`。
4. **输入校验在修改 scene 之前**：`build_character` 先调用 `mesh_data()`（内部 `validate()`），无效 spec 不创建任何对象。
5. **Inventory**：导出时写 `<name>.inventory.json`（metres），ICD Graph 用它与 FEV canonical 比较。

## Risks

- Blender re-import 的 action 起始帧偏移 1（FEV Negative Finding）；下游只依赖 frame length。
- Interchange import path 未验证；ICD 只覆盖 legacy `FbxImportUI` path。
