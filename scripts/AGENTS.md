# scripts — Deploy 脚本

本目录只保存把既有产物同步到目标运行环境的 Deploy 命令脚本。

## 允许

脚本必须同时满足：

1. 文件名以 `deploy-` 开头，或职责明确为 Deploy；
2. 只部署或同步已有产物，不生成、转换或分析资产；
3. 可重复执行，并允许通过参数覆盖目标路径。

## 禁止与路由

| 内容 | 正确位置 |
|------|----------|
| 调研、说明 | `docs/<YYYY-MM-DD>-<topic>/` |
| OpenSpec workflow | `openspec/` |
| 子项目业务脚本 | 对应 `repos/<project>/`，并遵循其变更流程 |
| Cook、host transform、实验脚本 | 对应 `pipelines/graphs/<domain>/<slug>/scripts/` |
| 临时一次性命令 | 终端执行，不落盘 |

**MUST NOT** 在本目录放置业务逻辑、Blender / `bpy` 工具、build、test、lint、analysis、research、data conversion 或配置样板。

Deploy 脚本可以被 Graph Invoke，但不会因此获得 Graph、Cook 或业务实现的 authority。
