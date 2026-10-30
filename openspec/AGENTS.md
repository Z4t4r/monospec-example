<!-- bmad:context -->

# openspec — Product SHALL 与 Change

`openspec/` 是产品 requirement、active spec、change proposal 与 immutable archive 的 authoritative subtree。项目背景见 [`project.md`](project.md)；active truth 在 `specs/`，执行中的 change 在 `changes/`。OpenSpec task checkbox 不是 Capability delivered claim。

## Policy

- 创建、评审、实施或归档 change 前，先读 [`../traits/icd-trait.md`](../traits/icd-trait.md) 与 [`../traits/ced-trait.md`](../traits/ced-trait.md)。
- Capability completion 必须按 ICD L1–L4 和对应 Evidence 判断；不得因 `tasks.md` 全部勾选就宣布 delivered。
- failure、defer、reorder 与 legal Stop Condition 由 CED 决定；CED 不得把 ICD FAIL 改写成 PASS。
- reusable finding 可以链接或提炼到 `docs/`，但 DOCS 不是 authoritative Epic state store。
- 从 DOCS Evidence Analysis 进入业务时，必须先取得明确的 Human Promotion Decision。Pipeline PASS、Agent Recommendation 或 DOCS `CONFIRMED` 均不得替代 `APPROVED`。
- Python 实现遵守 [`../traits/python-dialect-trait.md`](../traits/python-dialect-trait.md)；Acceptance Graph 遵守 [`../pipelines/AGENTS.md`](../pipelines/AGENTS.md)。

## Blocker Local Policy

关键事实未证实，或修复会打穿已验证基线时，必须先按 FEV 取得 Verdict，再按 CED 决定继续、隔离、defer 或合法停止。

- Pattern A：通过 gate 送到已验证的旧路径。
- Pattern B：调用即明确报错，并写明原因。
- Pattern C：在 proposal / spec 标记 `Out-of-Scope` 或 `Decision Needed`。

Pattern C 条目不得在 `tasks.md` 勾成完成。任何 Pattern 都不得用空返回、假成功、主路径占位算法或状态措辞，把 blocked capability 伪装成 delivered。

## Change workflow

使用 OpenSpec CLI 1.3.1 的当前语法：

```powershell
openspec new change <change-name>
openspec status --change <change-name>
openspec instructions apply --change <change-name>
openspec validate <change-name> --strict
openspec archive <change-name>
```

- change id 使用 lowercase kebab-case，并以动词开头，例如 `add-animation-support`。
- proposal 说明 Why、What Changes、Capabilities 与 Impact；delta spec 使用 `ADDED`、`MODIFIED`、`REMOVED` 或 `RENAMED` requirements。
- scenario 标题使用 `#### Scenario:`，并以 WHEN / THEN / AND 描述 observable behavior。
- implementation 中发现 design issue 时先更新 authoritative artifact；不得让实现与 spec 静默分叉。
- Human 通过自然语言和 artifact reference 确认 Promotion `APPROVED` 后，Agent 应创建或更新 change，无需用户调用专用命令；proposal 必须链接 DOCS analysis 与稳定 Pipeline Evidence。
- OpenSpec 只引用 Evidence，不复制完整 Run output；change 自己持有 normative `SHALL`、scenarios、scope 与 tasks。
- archive 前必须 strict validate，并核对 Capability Acceptance、Evidence 与 Deferred Blocker，而不只核对 task checkbox。

## Archive immutability

`openspec/changes/archive/` 是只读历史记录，一经 archive 即冻结。

- **MUST NOT** 因同步 spec、重命名、重构或事后措辞修正而回填 archive 中的 proposal、tasks、spec delta 或 metadata。
- 当前事实只在 `openspec/specs/`；archive 仅用于追溯 change 发生时的原始事实。
- archive 后需要纠错时，新建 change proposal；不要直接修改历史记录。

## Completion checks

- `openspec validate <change-name> --strict` 通过。
- spec delta 与 scenario format 有效，内部链接可解析。
- ICD Acceptance claim 可追溯到对应 Evidence；blocked capability 仍明确 undelivered。
- CED completion / defer state 位于 Epic 的 OpenSpec 或 project engineering trace，而不是 DOCS。
- DOCS-originated change 可追溯到 Human Promotion Decision、Evidence Analysis 与 stable Pipeline Run。
- archive 目录未被回填修改。

<!-- /bmad:context -->
