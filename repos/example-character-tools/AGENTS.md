# example-character-tools — Agent 入口

示例业务项目：Blender 5.1 add-on + headless CLI，生成示例角色并导出 UE5-ready FBX。它和主仓一起分发，用于展示 OpenSpec change 如何落到 `repos/`；目标项目可以删除。

- Contract：[`../../repos-meta/example-character-tools/AGENTS.md`](../../repos-meta/example-character-tools/AGENTS.md)。
- 行为来源：Root FEV `example-char`（[aggregate report](../../pipelines/graphs/example/example-character-export-fev/aggregate/report.md)）；需求：[OpenSpec change](../../openspec/changes/add-example-character-export/proposal.md)。
- `example_character_tools/spec.py` 不 import `bpy`，用 host CPython 测试：`python -m unittest discover -s tests`。
- `blender_export.py` / `operators.py` 只在 Blender 内运行；headless 入口为 `cli/export_character.py`，必须带 `--background`。
- 修改 unit、axis 或 FBX 设置前，先更新 OpenSpec 并重跑 ICD Graph `example-character-export-acceptance`。
