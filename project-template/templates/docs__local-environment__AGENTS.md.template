# local-environment — 本机 Blender / UE 操作入口

本目录保存环境 discovery 方法，不复制来源的 installation / account / process state。先读唯一 Topic Summary：[00-environment.md](00-environment.md)。父级 [docs policy](../AGENTS.md) 与 [根入口](../../AGENTS.md) 继续适用。

- MUST 在使用前核对 executable、project、version、session 与 readiness，再决定是否 launch。
- 启动、复用、重启 UE5.8 Editor，绑定 MCP，执行 UBT / MRQ，或终止 UnrealEditor 进程前，MUST 先读 [AIAGENT Windows Session Isolation](../../traits/aiagent-windows-session-isolation-trait.md)：Human Desktop Protection 优先；仅管理已确认归属的 Worker。
- 操作任何外部 Blender / UE workspace 时，MUST 显式读取其适用的 `AGENTS.md`，以及对应 `repos-meta/<project>/AGENTS.md`；不继承来源 workspace 路径。
- MUST NOT 仅凭 process、plugin enable flag 或历史记录宣称 MCP 可用、项目已加载或任务成功。
- MUST NOT 无差别 terminate Editor，不得关闭或重启 Human Editor。
- Local executable、project path、Worker identity 与 endpoint 放 `.local/`；凭据只进入 gitignored private config，不进入 tracked policy / Evidence / commit。
- 记录实际 version 与适用条件；本包保留的 Blender 5.1 / UE5.8 contract 不证明目标环境已满足。版本不匹配时先报告并验证，不能静默跳过约束。