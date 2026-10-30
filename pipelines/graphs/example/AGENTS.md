# example — Blender / UE5 示例 Graph domain

范围：`monospec-example` 自带的完整示例。角色由脚本生成，不依赖外部资产；用于展示 FEV → DOCS → Promotion → OpenSpec → ICD 的完整链路。

## Local Policy

- 继承 [Pipeline Local Policy](../../AGENTS.md) 与 [Pipeline Trait](../../../traits/pipelines-trait.md)。
- Blender 只用 `--background`（[`host_run/blender.py`](../../_shared/host_run/blender.py)）；UE5.8 只在每个 Run 新建的 AIAGENT Worker 中运行，并持有 `fev_parallel` lease（[`host_run/ue_worker.py`](../../_shared/host_run/ue_worker.py)）。先读 [AIAGENT isolation Trait](../../../traits/aiagent-windows-session-isolation-trait.md)。
- 本机路径与凭据只来自 gitignored `.local/environment.yaml`；tracked 文件不写 machine path。
- 新 domain 的目标项目可以删除本 domain；删除时同步更新 [pipelines/AGENTS.md](../../AGENTS.md) 的 registry 与示例 Topic 的链接。

## Active index

| slug | family | kind / scope |
|---|---|---|
| [example-character-export-fev](./example-character-export-fev/) | probe | Graph（Root FEV `example-char`：Blender 5.1 headless export → UE5.8 AIAGENT import；Aggregate 见 `aggregate/report.md`） |
| [example-character-export-acceptance](./example-character-export-acceptance/) | compose | Graph（ICD 验收：OpenSpec `add-example-character-export` 的 production 实现，与 FEV canonical 比较） |
