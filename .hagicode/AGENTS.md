# .hagicode — MonoSpec Host Configuration

遵循根 [AGENTS.md](../AGENTS.md)。本目录声明主仓可侧载的业务项目；业务代码位于 `repos/`，不是主仓的源码副本。

- [`monospecs.yaml`](monospecs.yaml) 保存 `version`、`repo_dir`、`commit_when_archive` 与 `repositories`；保留 schema，不继承来源项目 registry。
- 每个实际侧载项目填写 `path`、`url`、`displayName`、`description`、`optional`、`tags`。`path` 使用 `repos/<project>`；`description` 指向 `repos-meta/<project>/`，该目录必须有 `AGENTS.md`。
- 本示例项目只注册 in-tree 示例 `repos/example-character-tools`（由本仓直接跟踪，不 clone）；目标项目可删除该条目并恢复为 `repositories: []`。注释示例不表示项目已注册或已 clone。
- 注册项不等于 clone / load / 授权改代码。Agent 先读主仓、metadata 与子仓适用的 `AGENTS.md`，再按用户任务操作。
- 不自动 clone 或修改 remote。URL 不得含 credential / token；private local path 存 `.local/`，不写入可分发模板。
- [`standard_words.yaml`](standard_words.yaml) 保留 glossary schema，初始没有业务用语。填充前加载 [standard-words Trait](../traits/standard-words-trait.md)，只从目标项目真实 source 提取词条。
- 本配置不代表 HagiCode app 已安装或已连接；目标环境需要自行核对支持的 schema 与使用方式。