# AIAGENT Windows Session Isolation

## Metadata

```yaml
trait:
  id: aiagent-windows-session-isolation
  version: "1.1.0"
  date: "2026-10-14"
  status: "Proposed"
  type: "Runtime Isolation Policy"
  platform: "Windows / Unreal Engine 5.8"
  dedicated_windows_user: "AIAGENT"
```

Trait：Agent 在 Windows 上执行 UE5.8 自动化时，隔离 `AIAGENT` 运行环境，保护 Human Desktop。

> 适用范围：本机 Windows 上的 UE5.8 Editor、UnrealBuildTool、MCP、Commandlet、MRQ、自动化测试与 Worker 生命周期  
> 加载时机：启动 / 复用 / 重启 Worker Editor，绑定 MCP，执行 C++ 编译，或进行可能干扰 Human Desktop 的 UE 自动化之前 **MUST** 先读全文  
> 同步范围：本 trait 只留在 monospec `traits/`；**MUST NOT** 同步到 `repos/*/traits/` 或子仓业务树  
> 本机操作入口：[`../docs/local-environment/AGENTS.md`](../docs/local-environment/AGENTS.md)

## 1. Core Philosophy

**Isolate Agent Execution, Preserve Human Interaction.**

Agent 的自动化执行不得干扰人类当前 Windows 桌面。

`AIAGENT` 是专门用于 Agent 自动化工作的 Windows 用户身份。Agent 应在该用户拥有的独立运行环境中执行 UE5.8 Editor、MCP、C++ 编译、自动化测试和 MRQ 渲染。

基本原则：

- **Human Desktop First**：人类桌面拥有最高交互优先级。
- **Agent-Owned Lifecycle**：Agent 只能管理自身拥有的进程。
- **Session Isolation**：GUI 自动化尽可能运行于独立 Windows 用户会话。
- **Workspace Isolation**：Agent 与 Human 的项目写入环境相互隔离。
- **Minimal Interference**：避免窗口抢焦点、无关进程终止和不必要的 Editor 重启。
- **Recoverable Execution**：Agent Worker 应支持健康检查、重连和恢复。

## 2. Environment Ownership

### Human Environment

Human 用户会话用于：

- Cursor / Codex 交互
- 浏览器与日常桌面操作
- Human UE5.8 Editor
- 人类观察、验收和决策

Agent 不得：

- 关闭或重启 Human Editor。
- 操作 Human Editor 的窗口和输入。
- 将 Agent Editor 显示到 Human 桌面。
- 主动抢占 Human 桌面焦点。
- 终止不属于 Agent 的进程。

### AIAGENT Environment

专用 Windows 用户名：

`AIAGENT`

负责：

- Worker UE5.8 Editor
- UnrealBuildTool / C++ 编译
- MCP Server 与自动化客户端
- Python / Commandlet 执行
- Movie Render Queue
- 自动化测试
- Evidence 和运行日志
- Worker 生命周期管理

AIAGENT 仅管理自身进程，不拥有 Human Editor 的生命周期控制权。

## 3. Windows Session Policy

### 3.1 Identity

- 使用独立本地 Windows 用户 `AIAGENT`。
- 默认使用标准用户权限。
- 不得长期依赖管理员权限。
- 不得把登录凭据写入任何 **tracked** 文件、Trait 正文、Evidence、commit 或共享文档。
- 本机允许将凭据放在 gitignored 的 `local/aiagent.yaml`（目录 `traits/local/`）；Agent 需要时再读取，不得回写到仓库。
- 不得修改系统 DLL 或绕过 Windows 会话限制。

### 3.2 Session Behavior

- Agent GUI 应运行在 AIAGENT 用户会话。
- Agent 进程不得依赖 Human 桌面的键盘、鼠标或窗口焦点。
- GUI 自动化只能操作 AIAGENT 会话内的窗口。
- 会话锁定、断开或切换后，不得假定 GUI 自动化仍然可用。
- 若独立 GUI 会话不可用，应优先采用无头执行方式。
- 不得通过强制切换 Human 会话来满足 Agent 的执行需求。

独立 Windows 用户不必然意味着系统支持两个并发交互式桌面。

## 4. Editor Lifecycle Policy

每个 Worker Editor 必须记录：

```yaml
worker:
  owner: AIAGENT
  pid: null
  session_id: null
  project_path: null
  execution_id: null
  start_time: null
```

### Startup

- 优先复用已运行且健康的 Worker Editor。
- 不得无理由重复启动 Editor。
- 启动前检查是否存在相同项目的 Worker。
- 避免产生孤立 Editor 进程。

### Shutdown

关闭前必须确认：

1. 进程归属用户为 AIAGENT。
2. Session ID 与 Worker 记录匹配。
3. PID 与启动记录匹配。
4. 项目路径与预期 Worker 一致。

禁止：

```powershell
taskkill /F /IM UnrealEditor.exe
```

不得无差别终止所有 UnrealEditor 进程。

优先正常退出；仅在必要时强制终止已确认归属的 Worker PID。

### Restart

- 重启范围仅限 AIAGENT Worker。
- 重启前释放相关 MCP 连接。
- 重启后恢复 MCP 连接。
- 恢复任务上下文与必要状态。
- 不得重启 Human Editor。

## 5. Build Policy

根据任务选择最小必要执行环境。

| Task | Preferred Mode |
|---|---|
| C++ 编译 | UnrealBuildTool |
| Python 静态检查 | Headless |
| 资源检查 | Commandlet |
| MCP Editor 操作 | Worker Editor |
| MRQ GPU 渲染 | GPU-capable Worker |
| DLL / 模块重载 | Controlled Worker Restart |
| Human 验收 | Human Editor |

规则：

- 编译不应默认导致 Editor 重启。
- 优先复用 Worker Editor。
- Live Coding 仅用于适合热更新的修改。
- 涉及不适合热更新的 C++ 变更时，允许重启 Worker。
- 不得为了 Agent 编译而关闭 Human Editor。
- 编译输出和插件 DLL 不得与正在使用的 Human Editor 产生非预期冲突。

## 6. MCP Isolation

MCP 应明确连接到 AIAGENT Worker，而不是自动选择任意 UE Editor。

要求：

- MCP Server 与 Worker 身份关联。
- MCP Client 使用明确的 Worker Endpoint。
- 多个 Editor 存在时不得依赖模糊的自动发现。
- Worker 重启后支持 MCP 重新连接。
- MCP 操作必须确认目标项目和目标进程。
- MCP 不得向 Human Editor 发送修改操作。

若无法确定 MCP 目标，停止该操作并报告原因。

## 7. Workspace Isolation

独立用户会话不代表项目文件天然隔离。

要求：

- Human 与 AIAGENT 使用独立的可写项目工作区。
- 不得并发修改同一份 `.uasset`。
- 避免共享正在使用的插件 DLL 和编译中间文件。
- 使用版本控制或明确的同步机制交换变更。
- 不得覆盖 Human 未提交的修改。
- Agent Evidence 和临时文件应独立存储。

推荐结构：

```text
Workspaces/
  Human/
    UEProject/
  AIAGENT/
    UEProject/

Evidence/
  AIAGENT/
    execution-id/
```

该结构是逻辑约定，不强制修改现有项目目录。

## 8. GPU and Rendering Policy

AIAGENT 可以使用主机 GPU 执行 UE5.8 渲染。

适用任务：

- Movie Render Queue
- Deferred Renderer
- GPU Skinning
- SceneCapture
- PNG Evidence

约束：

- GPU 是共享资源，不保证性能隔离。
- 不得假定 RDP、锁定会话或断开会话均支持正常 GPU 渲染。
- 优先使用能够稳定提供所需图形上下文的 Worker 执行模式。
- 渲染失败时保留日志，不得通过操作 Human 桌面强行恢复。
- Agent 应避免无必要的高 GPU 负载和重复渲染。

## 9. Recovery Policy

Worker 异常时，按以下顺序处理：

1. 检查 Worker 进程状态。
2. 检查 MCP 连接状态。
3. 尝试恢复连接。
4. 必要时重启 AIAGENT Worker。
5. 恢复可恢复任务。
6. 无法恢复时报告阻塞原因。

禁止通过重启 Human Editor、注销 Human 用户或重启整台主机作为默认恢复手段。

需要重启主机或改变 Human 会话状态时，必须获得人类明确批准。

## 10. Human Desktop Protection

Human Desktop Protection 是本 Trait 的最高优先级约束。

Agent 不得：

- 抢占 Human 输入焦点。
- 移动或关闭 Human 窗口。
- 注销 Human 用户。
- 锁定 Human 会话。
- 修改 Human 桌面显示配置。
- 无授权重启 Windows。
- 无差别终止 UE Editor。
- 通过 GUI 自动化操作 Human 桌面。

如果某项自动化必须违反上述约束才能执行，应停止该操作并说明原因。

## 11. Agent Integration

Agent 启动 UE5.8 相关自动化任务时，应遵循：

```text
Agent Task
    |
    v
Resolve Execution Mode
    |
    +-- Headless / UBT / Commandlet
    |
    +-- AIAGENT Worker Editor
              |
              v
         MCP / Rendering
              |
              v
         Artifacts / Logs
```

执行策略：

1. 优先选择不需要 GUI 的执行方式。
2. 需要 Editor 时优先复用 AIAGENT Worker。
3. 仅在必要时启动或重启 Worker。
4. 所有生命周期操作必须验证进程归属。
5. 不得影响 Human Desktop。
6. 将运行结果返回 Agent Orchestrator。

## 12. Trait Boundary

本 Trait 仅负责：

- Windows Agent 用户与会话约束
- Human / Agent 运行环境隔离
- UE5.8 Worker 生命周期
- MCP 目标隔离
- 编译与工作区隔离
- GPU 渲染运行约束
- 故障恢复
- 人类桌面保护

本 Trait 不负责：

- 具体业务功能实现
- UE 场景设计
- 动力学求解
- 项目验收流程
- Epic 任务拆分
- 项目管理
- Windows 系统安装教程

## 13. Core Invariants

以下规则始终成立：

**Invariant 1:** Agent 不得关闭 Human Editor。

**Invariant 2:** Agent 不得抢占 Human Desktop。

**Invariant 3:** Agent 只能管理已确认归属的 Worker 进程。

**Invariant 4:** MCP 必须明确绑定目标 Worker。

**Invariant 5:** Human 与 Agent 不得并发写入同一资产。

**Invariant 6:** Worker 重启不得导致 Human Editor 重启。

**Invariant 7:** Windows 会话能力不得被未经确认的假设替代。

**Invariant 8:** Human Desktop Protection 优先于 Agent 自动化任务完成。

---

**Final Principle**

AIAGENT owns its execution environment.

Human owns the interactive desktop.

Agent automation must never compromise human desktop stability.
