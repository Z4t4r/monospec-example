<!-- bmad:context -->

# MonoSpec Example — Agent 入口

本项目名为 `monospec-example`，作为可复用的 MonoSpec 示例项目与后续项目模板维护。示例内容用于展示 research、FEV、DOCS 与 ICD 的协作方式；示例结果不代表新项目已完成验证。目标项目采用模板时，应按自己的需求与环境更新配置和执行 Evidence。

跨阶段 investigation 如何连接目标、FEV 实验、DOCS 回填、Promotion 与 production ICD，可参考示例 Topic [`docs/2026-10-30-investigation-workflow-example/`](docs/2026-10-30-investigation-workflow-example/00-调研总览.md)。该 Topic 是 `PENDING_VALIDATION` 的非规范 reference，其中的 skill 草案未安装；现行规则仍以本文件、subtree `AGENTS.md` 与 Trait 为准。

可运行的完整案例见 [`docs/2026-10-30-example-character-blender-ue5/`](docs/2026-10-30-example-character-blender-ue5/00-调研总览.md)：脚本生成的角色经 Blender 5.1 headless 导出、UE5.8 AIAGENT Worker 导入，覆盖 FEV、Promotion、OpenSpec、`repos/example-character-tools` 与 ICD。示例不含外部资产；本机路径只放在 gitignored `.local/environment.yaml`。示例 domain、change 与 `repos/example-character-tools` 均可在目标项目中删除。

本仓是可侧载多个业务项目的 MonoSpec host；业务源码位于 `repos/`，项目注册由 `.hagicode/monospecs.yaml` 管理。本仓用于组织 Blender / UE5 相关 research、可 cook 验收 Graph、产品规格与子仓元数据。根 `AGENTS.md` 是 repository-wide policy 与 cross-tree routing 的唯一入口；各专业子树的额外规则由其同级 `AGENTS.md` 负责。Trait 的完整 discovery / trigger map 在 [`traits/AGENTS.md`](traits/AGENTS.md)。

## Policy

- **MUST NOT** 使用根 `README.md` 作为约定入口；若存在根 `CLAUDE.md`，只允许指向本文件，不得另立规则源。
- 修改任何专业子树前，先读该目录的 `AGENTS.md`；任务命中 Trait trigger 时，再按 [`traits/AGENTS.md`](traits/AGENTS.md) 加载 Trait 全文。
- 新建或改写中文技术内容时加载 [`traits/chinese-technical-writing-trait.md`](traits/chinese-technical-writing-trait.md)：简单骨架用常用中文，domain topic、专用名词 / 动词与复杂机制保留英文。
- 本项目禁用 `gds-quick-dev`（其 workflow 与本项目规范冲突）。Agent **MUST NOT** 因其 description、自动 trigger、其他 skill routing 或历史会话继续加载或执行该 skill；后续工作按本仓 `AGENTS.md`、适用 Trait 与 subtree contract 执行。

## Where things are

| 职能 | 入口 |
|------|------|
| 可 cook 验收 Graph | [`pipelines/AGENTS.md`](pipelines/AGENTS.md) |
| Agent 行为契约与 Trait discovery | [`traits/AGENTS.md`](traits/AGENTS.md) |
| Research / reusable project knowledge | [`docs/AGENTS.md`](docs/AGENTS.md) |
| 本机 Blender / UE discovery 与 launch | [`docs/local-environment/AGENTS.md`](docs/local-environment/AGENTS.md) |
| 产品 SHALL、change 与 archive | [`openspec/AGENTS.md`](openspec/AGENTS.md) |
| 部署等允许脚本 | [`scripts/AGENTS.md`](scripts/AGENTS.md) |
| 子仓 Agent / 描述元数据 | [`repos-meta/AGENTS.md`](repos-meta/AGENTS.md) |
| MonoSpec 侧载配置 | [`.hagicode/AGENTS.md`](.hagicode/AGENTS.md) |
| Portable bootstrap / 历史 revision inputs | [`bootstrap/AGENTS.md`](bootstrap/AGENTS.md) |
| Repository policy automation | [`.github/AGENTS.md`](.github/AGENTS.md) |

## Cross-tree boundaries

- 在本机查找、启动或操作 Blender / UE 时，先读 [`docs/local-environment/AGENTS.md`](docs/local-environment/AGENTS.md)，再显式读取目标 workspace 与侧载项目适用的 `AGENTS.md`。仓库外文件不会因本入口存在而自动加载。

- Research / Project Memory 落在 `docs/<topic>/`；现有 dated Topic 保持有效。现行验收落在 `pipelines/graphs/<domain>/<slug>/`；产品能力与正式 change 落在 `openspec/`。
- 业务代码在 `repos/`；pipeline script 默认保持隔离，只有经 OpenSpec 明确纳入后才进入业务代码。
- Cook runtime 是 Python（`pipelines/_shared/cook_runtime/`）；**MUST NOT** 为本仓 pipeline 引入 Node / TypeScript runtime。
- 根规则只定义跨树边界；subtree Local Policy 只能 strengthening / narrowing 对应 Trait，不能弱化其 Core Philosophy、转移 authority 或静默解决真实冲突。

## Automatic Git commit

成功完成会修改 repository tracked content 的任务后，Agent **MUST** 自动创建 Git commit，不需要等待用户再次确认。该授权只覆盖 commit，不覆盖 push。

提交前必须同时满足：

- 用户请求的工作已经完成；
- 与变更风险相称的 validation 已通过；
- 不存在 unresolved failure、blocking issue 或待 Human Decision；
- commit 只包含当前任务产生或用户明确授权包含的变更。

Agent 必须：

1. 开始修改前读取 `git status --short`，记录 pre-existing changes；
2. 只 stage 当前任务拥有的文件，不得把无关 user changes 纳入 commit；
3. 使用简洁的 Conventional Commit message；
4. commit 后确认工作区只剩 pre-existing changes；
5. 在最终回复中报告 commit SHA 与 message。

Agent **MUST NOT**：

- 自动执行 `git push`；只有用户明确要求 push 时才能执行；
- 自动执行 amend、rebase、merge、force push 或 history rewrite；
- 为 read-only、讨论、评审、失败、未完成或没有文件变化的任务创建 commit；
- 在变更归属不明确时 commit；
- 创建 empty commit；
- 使用 `git add -A`，除非任务开始时工作区干净且全部变更均属于当前任务。

用户在当前任务中明确要求不 commit 时，该要求覆盖本节。若任务必须触达已有 user change 且无法安全拆分，Agent 不得自动 commit，并必须报告原因。

<!-- /bmad:context -->
