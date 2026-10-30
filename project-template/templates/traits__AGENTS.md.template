<!-- bmad:context -->

# traits — Agent 行为契约

本目录保存跨变更、跨子树仍生效的 Agent behavior contract。人与 Agent 的目录入口均为本文件；**MUST NOT** 使用 `README.md`。任务命中下表 trigger 时，先读对应 Trait 全文再行动。

## Policy

- Trait 定义 general semantics；subtree `AGENTS.md` 只定义对应目录的 Local Policy。
- Local Policy MAY 缩小适用范围、把 SHOULD 提升为 MUST，或增加安全、工具、evidence、命名、workflow 与 carrier 约束。
- Local Policy **MUST NOT** 弱化 Trait、反转 Core Philosophy、重定义 authority、允许 Trait 禁止的行为，或接管其他 Trait 的职责。
- 无法解释为 strengthening / narrowing 的差异必须显式标为 conflict；解决前不得静默选择一方或报告完成迁移。

## Trait discovery

| Trigger | MUST 先读 |
|---------|-----------|
| 新建 / 改写目录入口、索引或脚手架 | [`agents-md-only-trait.md`](agents-md-only-trait.md) |
| 多个实现、库、API、算法、依赖、模型或 runtime 之间选型 | [`technology-first-trait.md`](technology-first-trait.md) |
| Requirements、Research 或 candidate discovery | [`bmad-trait.md`](bmad-trait.md) |
| 未证实技术事实、feasibility experiment、Evidence 或 Verdict | [`fev-trait.md`](fev-trait.md) |
| 声明或评审 Capability Acceptance L1–L4 | [`icd-trait.md`](icd-trait.md) |
| Epic failure、defer、reorder、continuation 或 Stop Condition | [`ced-trait.md`](ced-trait.md)（PENDING） |
| 新建或维护 reusable Project Knowledge | [`docs-trait.md`](docs-trait.md)（PENDING） |
| 新建、改写或 cook `pipelines/graphs/**` | [`pipelines-trait.md`](pipelines-trait.md) + [`../pipelines/AGENTS.md`](../pipelines/AGENTS.md) |
| 编写或修改 `.py` | [`python-dialect-trait.md`](python-dialect-trait.md) |
| Blender 角色 Soft Realistic Anime render | [`soft-realistic-anime-render-trait.md`](soft-realistic-anime-render-trait.md) |
| 标准用语或 glossary | [`standard-words-trait.md`](standard-words-trait.md) |
| 新建 / 改写中文技术内容，或用中文描述程序行为 / CLI | [`chinese-technical-writing-trait.md`](chinese-technical-writing-trait.md) |
| Blender / UE5 的 bone、rigid body、IK、animation evaluation、physics writeback 或 space conversion | [`transform-space-expert-trait.md`](transform-space-expert-trait.md) |
| Blender Armature / Bone / PoseBone / constraints / IK / depsgraph 或最终 pose | [`blender-animation-domain-expert-trait.md`](blender-animation-domain-expert-trait.md) |
| UE5 FTransform / CompactPose / AnimGraph / Skeletal Control / Physics writeback | [`ue5-animation-domain-expert-trait.md`](ue5-animation-domain-expert-trait.md) |
| rigid body / constraint / collision / solver / Chaos / Blender Rigid Body / physics QA | [`physics-domain-expert-trait.md`](physics-domain-expert-trait.md) |
| Windows `AIAGENT` 会话、UE5.8 Worker Editor 生命周期、MCP Worker 绑定、Agent 编译 / MRQ，或可能干扰 Human Desktop 的 UE 自动化 | [`aiagent-windows-session-isolation-trait.md`](aiagent-windows-session-isolation-trait.md) |

组合场景：

- 未证实的生产路径或跨域链变更：FEV + CED + 对应 subtree Local Policy。
- OpenSpec change 的创建、评审、实施或归档：ICD + CED + [`../openspec/AGENTS.md`](../openspec/AGENTS.md)。
- Blender ↔ UE 工作：transform-space，并叠加对应 engine / physics Trait。
- 本机 launch / 复用 / 重启 UE5.8 Editor、绑定 MCP、UBT 编译或 MRQ：AIAGENT Session Isolation + [`../docs/local-environment/AGENTS.md`](../docs/local-environment/AGENTS.md)。

## Boundaries

- 本目录不落盘 `README.md`。
- 编排仓 Trait 不默认同步到 `repos/*/traits/`。
- 已退役版本只保留在 `archive/`；archive 内容是 non-normative history。Bootstrap 不复制来源历史。
- 本机 secrets（如 AIAGENT 凭据 `.local/aiagent.yaml`）统一放在仓库根 gitignored 的 `.local/`，不放在 `traits/` 下；**MUST NOT** commit、同步或把其中凭据复制进 tracked Trait / docs / Evidence。

<!-- /bmad:context -->
