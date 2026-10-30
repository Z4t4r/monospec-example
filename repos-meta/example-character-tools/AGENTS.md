# repos-meta / example-character-tools

| 项 | 内容 |
|---|---|
| 源码 | [`repos/example-character-tools/`](../../repos/example-character-tools/AGENTS.md)（in-tree 示例，`.gitignore` 例外放行；不是独立 clone） |
| 职责 | 示例角色的 `CharacterSpec`、Blender build、FBX export、add-on Operator 与 headless CLI |
| 可写范围 | 仅在对应 OpenSpec change 的 tasks 范围内修改 |
| 适用 Trait | [python-dialect](../../traits/python-dialect-trait.md)（`spec.py`：host CPython；其余：`blender-addon`）、[blender-animation-domain-expert](../../traits/blender-animation-domain-expert-trait.md)、[transform-space-expert](../../traits/transform-space-expert-trait.md)、[ICD](../../traits/icd-trait.md) |
| Validation | `python -m unittest discover -s tests`（项目目录内）；Capability 由 [ICD Graph](../../pipelines/graphs/example/example-character-export-acceptance/pipeline.md) 验收 |
| 上游边界 | 不依赖第三方 Blender add-on；不随包分发资产 |
