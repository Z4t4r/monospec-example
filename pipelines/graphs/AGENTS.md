# graphs — Graph Workspace

遵循 [`../AGENTS.md`](../AGENTS.md)。Bootstrap 本身不安装 Active Graph；本示例项目另带 `example` domain（见 [`example/AGENTS.md`](example/AGENTS.md)）。

Domain registry 的唯一入口是 [`../AGENTS.md`](../AGENTS.md)，本文件不维护第二份 registry。新增 domain 时在该入口登记，并创建 `<domain>/AGENTS.md`；domain 入口保存 scope、Local Policy 与 Active Graph index。

每个 Graph 使用 `<domain>/<slug>/pipeline.md`，不得把 template 或无完整 contract 的 draft 标为 Active。只在实际创建 domain / Graph 时增加条目，不创建虚假 Graph。
