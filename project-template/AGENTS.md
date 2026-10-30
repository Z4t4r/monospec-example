# project-template — Portable Bootstrap

本 package 把完整现行 Trait、MonoSpec host 结构和 Blender / UE5 工作约定安装到其他项目。入口是 `install.ps1`，部署只依赖 PowerShell 7；运行已部署的 Python helper 时另需目标环境的 CPython。Installer 不安装软件，也不要求联网。

## Install

把整个 `project-template/` 复制到目标项目以外的位置，保留 `manifest.json`、`install.ps1` 和 `templates/` 的相对位置。目标项目 Agent 先读其已有 `AGENTS.md`，再运行：

```powershell
pwsh -NoProfile -File ./project-template/install.ps1 -Target ../target-project -WhatIf
pwsh -NoProfile -File ./project-template/install.ps1 -Target ../target-project
```

`-Target` 必填，可指定尚不存在的目录。默认先检查所有 destination：不存在则计划新建，内容相同则保留，内容不同则报 `CONFLICT` 并在写入前退出。没有 overwrite / force 模式。`-WhatIf` 只输出计划，不创建目标目录。成功输出 `INSTALLED` 或 `UNCHANGED`；失败返回 non-zero exit code。

目标中已有 `AGENTS.md`、`.gitignore` 或其他同名文件时，Agent 必须先处理冲突：根据目标项目的真实规则人工 merge，再在独立空目录安装并比较所需内容。不得为了让 installer 通过而删除目标文件。Installer 不自动 merge policy，不自动 commit、push、下载依赖或启动应用。根 AGENTS template 保留来源的 Automatic Git commit policy；目标 Agent 采用前须核对既有规则与任务授权，不能把 installer 成功解释为 push 授权。

`2.0.0` 替换 `1.0.0` 的精简版 Trait，旧目标必须在独立目录生成完整版后 merge。旧版 `engineering-trait.md`、`authoring-trait.md`、`transform-trait.md`、`blender-trait.md`、`ue5-trait.md` 不再分发；目标 merge 时将这些旧文件和 trigger 引用迁到原名完整 Trait，避免双入口。Installer 不自动删除已有文件。

安装后，目标 Agent 读取根 `AGENTS.md`；本机软件位置、版本、Worker、资产路径按 `docs/local-environment/AGENTS.md` 在目标环境重新发现。安装成功仅说明 scaffold 已部署，不表示 engine、MCP 或 Cook 可用。

## Payload

| 目标 | 内容 |
|------|------|
| `AGENTS.md`、`CLAUDE.md`、`.gitignore` | 根入口、单一指针、本机数据 ignore |
| `traits/` | 原名完整的 17 个通用 / Blender / UE5 Trait 与 discovery map |
| `.hagicode/` | MonoSpec 侧载 registry schema、空业务清单、glossary schema 和入口 |
| `docs/`、`docs/local-environment/` | Research / Project Knowledge、本机 discovery 边界 |
| `pipelines/`、`pipelines/graphs/`、`pipelines/_shared/`、`pipelines/_template/` | 完整 Pipeline contract、cook_runtime、FEV coordinator / schemas / tests 和未激活 Graph template |
| `openspec/`、`openspec/specs/`、`openspec/changes/` | 产品 SHALL、change、只读 archive 的目录约定 |
| `repos/`、`repos-meta/` | 业务树占位入口、子仓 metadata 约定 |
| `scripts/`、`bootstrap/` | Deploy 与 bootstrap 约定 |
| `.cursor/skills/pipelines-cook-invoke/` | canonical Invoke 查重与同 Socket 微调 contract |
| `.github/` | DOCS policy validator、workflow、空 link baseline |

不复制来源业务项目 registry、glossary 词条、Active Graph、Run、Research、产品 spec、子仓、资产、business script、MCP config、Git history、机器路径、凭据、lease state、cache 或历史 validation report。领域内容只保留 Blender / UE5，剔除专属格式集成 Trait 及其相关段落；混合段落只替换相关示例，不删除通用规则。

完整 Trait 包含：`agents-md-only`、`technology-first`、`bmad`、`fev`、`icd`、`ced`、`docs`、`pipelines`、`python-dialect`、`soft-realistic-anime-render`、`standard-words`、`chinese-technical-writing`、`transform-space-expert`、`blender-animation-domain-expert`、`ue5-animation-domain-expert`、`physics-domain-expert`、`aiagent-windows-session-isolation`。保留来源 metadata 的 version / status，未提升 maturity。

FEV 保留全部 35 节（含 Hierarchical / Parallel Investigation、Run delivery、Artifact Value、Retention）；ICD 保留全部 19 节与 L1–L4。BMAD、CED、DOCS、technology-first、standard-words 正文与来源相同。Blender 原 §12 / §30、UE5 原 §42 / §43、Physics 原 §37 属于被排除集成，整节移除；其余 heading 保留原编号，便于 diff 与追溯。

[`source-map.json`](source-map.json) 记录 source revision、逐文件 normalized SHA-256、原文 / template 行数、heading 保留数与排除 section number。除领域剔除外，仅对业务名称、本机绑定、历史链接和相应目录路由做 portable adaptation；不再用摘要替代完整机制。

MonoSpec host 通过 `.hagicode/monospecs.yaml` 注册多个 `repos/<project>/`，`description` 指向 `repos-meta/<project>/`；保留 `version`、`repo_dir`、`commit_when_archive` 和每个 repository entry 的全部字段结构。初始 `repositories: []`，使用注释示例填入目标项目真实注册项。不是单一业务源码仓，也不自动 clone registry 中的项目。

## Maintenance

- 本文件管 package；`templates/*.template` 是待部署数据，只在目标项目安装后成为 policy，不在源仓接管 authority。
- **MUST** 从对应完整 source 维护 template，同步更新 `manifest.json` 与 `source-map.json`；禁止递归扫描本仓生成 payload，禁止擅自摘要化。
- **MUST NOT** 加入实际业务名称、账号绑定、凭据、绝对路径、资产、Evidence 或历史状态。`AIAGENT` 是隔离 Trait 声明的逻辑 Worker identity，不代表复制了来源机器账号或凭据。
- **MUST NOT** 在 package 中保留未使用的 template。新增内容必须通过 privacy / link / installation tests。
- Manifest version 使用 SemVer；变更 template 或 installer 的发布行为时更新版本。当前 `2.0.0`。
- 更新不覆盖已有目标文件；有 drift 时按目标项目变更流程 merge，不把重装当作 upgrade migration。

## Validation 与分发

```powershell
pwsh -NoProfile -File ./bootstrap/project-template/tests/run-tests.ps1
pwsh -NoProfile -File ./bootstrap/project-template/tests/run-tests.ps1 -SourceRoot . -PythonExecutable python
Compress-Archive -Path ./bootstrap/project-template -DestinationPath ./project-template.zip
```

只分发此 package 或上述 ZIP，禁止把源仓、`.git/`、本机配置或未审核目录一同打包。Tests 检查空目录安装、重复安装、conflict preflight、WhatIf、path traversal、symlink / junction、payload privacy、内部链接、完整 Trait 保留和 MonoSpec schema。`-SourceRoot` 额外检查来源 hash、FEV 全部机制原文和 ICD 仅改变领域示例；`-PythonExecutable` 在安装后的隔离目标中执行 FEV P0–P8、Evidence helper tests 和 DOCS validator。P9 live Editor / MCP 不随包宣称通过。

写入期间的磁盘 / 权限错误可能留下部分新文件；修复后可重跑，已有不同内容仍会被保留。
