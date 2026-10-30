# bootstrap — Installation Contract

遵循根 [AGENTS.md](../AGENTS.md)。本目录只保存当前项目的安装约定，不复制来源历史 Bootstrap Specification。

- Portable package 包含完整现行通用、Blender / UE5 Trait 与其显式 runtime / policy dependencies；只按 manifest 部署，不递归 export 项目数据。
- 独立 package 的 `AGENTS.md` 说明 `install.ps1 -Target <directory>`、WhatIf 与 conflict preflight；来源项目不需要存在于目标机器。
- 已有文件发生 drift 时按目标项目 workflow merge，不得强制覆盖。旧版精简 package 升级到完整版同样必须先处理 conflict，不能在现有 policy 上自动混装。
- 安装仅部署规范 / helper，不代表 engine、MCP、HagiCode 或 OpenSpec CLI 已可用；须在目标环境重新发现并验证。