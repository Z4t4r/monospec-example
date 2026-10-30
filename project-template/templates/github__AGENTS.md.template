# .github — Repository Policy Automation

本目录只保存 repository-level CI workflow 与只读 policy validator。它执行既有 AGENTS / Trait / OpenSpec 约束，不拥有产品、Pipeline、DOCS 或业务 authority。

## Policy

- Python validator 使用 `repository-policy` dialect，落在 `scripts/`，只使用 standard library，并保持 read-only。
- Workflow 只能报告或阻止确定性 drift；不得自动修改 Topic、提升 knowledge state、批准 Promotion、签发 Acceptance 或改变 Trait maturity。
- historical debt 必须通过可审计 baseline 显式保留；新增 drift 必须失败，baseline 不得在 CI 中自动更新。
- 新 workflow 或 validator 必须在本地运行对应命令，并记录在调用它的 workflow 中。

## Commands

```powershell
python .github/scripts/validate_docs_topics.py
python .github/scripts/validate_docs_topics.py --strict-existing-links
```

默认命令允许 baseline 中已知的 legacy broken links，但会阻止新增 broken link。严格命令用于清理 legacy debt。
