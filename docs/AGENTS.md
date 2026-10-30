<!-- bmad:context -->

# docs — Research 与 Project Knowledge

`docs/` 保存 technical research、investigation、guide、reference、walkthrough 与 reusable project knowledge。通用 knowledge semantics 由 [`../traits/docs-trait.md`](../traits/docs-trait.md) 定义；本文件只保留 docs subtree 的 strengthening / narrowing。`docs/` 不是源码的第二份实现，也不是 OpenSpec、ICD、CED 或 pipeline state 的 authoritative store。

## Policy

- 在 `docs/` 新建或改写 reusable knowledge 前，先读 [`../traits/docs-trait.md`](../traits/docs-trait.md)。
- 产品 SHALL 与正式 change 留在 `openspec/`；现行 cook / Acceptance Evidence 留在 `pipelines/`；Epic state 与 Deferred Blocker 留在其 OpenSpec / project engineering trace。
- Local Policy 只能加强或缩小 DOCS Trait；不能改变 authority。发现真实冲突时必须明确记录并解决，不得静默选择。
- 不要在当前任务之外扩大 scope，也不要创建 backlog artifact。独立问题只有在用户明确授权后才进入对应 OpenSpec / project workflow。

## Topic read contract

- 用户引用 Topic directory 时，先读该目录唯一的 `00-*.md` Topic Summary，再按任务读取必要的 Decision、Finding、Evaluation、Pipeline Design 或 Evidence Analysis；**MUST NOT** 默认读取整个目录或全部 Session Snapshot。
- 用户引用具体 Markdown 时，该文件是 primary context；只有关联内容可能改变当前结论时才继续展开。
- 新建或触达改写的 Topic Summary 必须优先给出当前结论、knowledge state、lifecycle、applicability、authority、关键 Evidence 与 supporting document links；未触达 historical Topic 通过后续渐进迁移补齐。
- `SESSION_SNAPSHOT` 只保存 conversation synthesis；不得因被写入 DOCS 自动成为 `CONFIRMED` knowledge。
- Knowledge state 使用 `CONFIRMED`、`INFERRED`、`UNKNOWN`、`PENDING_VALIDATION`；lifecycle 独立使用 `ACTIVE`、`STALE`、`SUPERSEDED`、`HISTORICAL`。

## Research layout

- 新的独立 research 使用 `docs/<YYYY-MM-DD>-<topic>/`。
- 每个 Topic directory 必须包含 `topic.yaml`，只保存目录级 metadata：`topic`、`created`、`updated`。日期使用 `YYYY-MM-DD`；Topic 中的 durable content 发生修改时同步更新 `updated`。
- 每个 dated research directory 必须有 `00-调研总览.md`；不要为了编号创建空文件。
- `00-调研总览.md` 至少包含：目的、范围、核心结论、关键发现、文档索引；只有确有 unresolved item 时才增加未解决问题。
- 补充文件按需要编号，例如 `01-使用指南.md`、`02-技术参考.md`、`03-快速参考.md`、`04-实验记录.md`、`05-问题与结论.md`。

## Local conventions

- 开始新 research 前先查找相关文档；同一结论优先 update / correct existing knowledge，而不是创建第二份 authoritative conclusion。
- 源码 evidence 使用仓库内可解析的相对路径，并同时指出最接近实际行为的 type / function / relevant behavior；不要只给路径。
- 文档间依赖使用从当前文件实际可解析的相对链接；移动文件时同步修复链接。
- 调研结论依赖环境、版本、命令或 experiment 时，记录足以复现 claim 的最小条件；不要复制无关环境详情。

## Pipeline handoff and promotion

- DOCS 中的 Pipeline Design 在 handoff 前保存 intended design；定稿时必须记录 target Graph、approved date、required Decision 与 `implementation_authority: PIPELINE`。
- handoff 后，Graph、script、Run 与 test 是 actual behavior authority。DOCS 保存 rationale、analysis 与 links，不成为第二套 Pipeline contract。
- `EVIDENCE_ANALYSIS` 必须区分 Observation、Interpretation、Conclusion、Unknown 与 Limitations，并引用 stable Pipeline Run identity；默认不复制完整 Run output。
- Pipeline PASS 不自动进入业务。Agent MAY 提出 Promotion Recommendation；只有 Human 明确确认 `APPROVED` 后，才创建或更新 OpenSpec change。
- OpenSpec change 引用 DOCS analysis 与 Pipeline Evidence，自行持有 normative `SHALL`、scenarios、scope 与 tasks。

## Completion checks

- Topic directory 包含有效的 `topic.yaml`，且 `topic` 与目录名一致。
- Topic directory 只有一个 `00-*.md` Topic Summary；目录引用遵循 progressive disclosure。
- dated research 使用正确目录和 `00-调研总览.md`。
- 关键 claim 的 evidence、knowledge state、scope 与适用版本满足 DOCS Trait。
- 内部链接可解析，敏感信息已脱敏。
- 没有重复 authoritative copy、越权保存 Epic state、扩大任务 scope 或创建替代 backlog。
- `python .github/scripts/validate_docs_topics.py` 通过；legacy broken links 由 baseline 显式保留，新 drift 必须失败。

<!-- /bmad:context -->
