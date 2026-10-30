# DOCS — Agent-Reusable Project Knowledge Layer

## Metadata

```yaml id="thz6nq"
trait:
  id: docs
  version: "0.10.0"
  date: "2026-09-22"
  status: "PENDING"
  type: "Knowledge Layer"
```

## Core Philosophy

**DOCS 是 Agent 可持续复用的通用项目知识层，也是有价值但无更明确归属信息的默认沉淀位置。**

DOCS 的核心目标不是：

> “把项目写成很多文档。”

而是：

> **让未来 Agent / Human 能够发现、理解、验证、引用、复用和维护项目知识。**

---

# 1. Purpose and Ownership

DOCS 是 Agent 可复用的 **Project Knowledge Layer**，保存具有持续工程价值、可发现、可验证和可维护的知识。它 MAY 接收 research、investigation、experiment、incident、source/runtime inspection、external reference、implementation experience 与 conversation synthesis 等来源，不使用严格内容类型白名单。

写入前 MUST 先判断 authority：

| 信息 | authoritative owner |
|---|---|
| Formal specification / change | OpenSpec |
| Feasibility Verdict | FEV |
| Capability Acceptance | ICD |
| Epic Execution State | CED |
| 当前程序行为 | Source / Runtime / Tests |
| 无更明确 owner、但有持续复用价值的知识 | DOCS |

更明确的 Engineering Owner 优先。DOCS MAY explain、summarize、reference、contextualize 或保存 reusable finding，但 MUST NOT 因复制或总结而改变原始 authority。

BMAD、FEV、ICD、CED、OpenSpec、Runtime、Tests、Agent/Human research 都 MAY 成为知识生产者；DOCS 不属于其中任何一个方法，也不是第二个 specification、acceptance、Epic tracker 或 implementation system。

---
# 2. Research First

在开始新的独立调研前，Agent SHOULD：

1. 检查已有 DOCS；
2. 查找相关 Research；
3. 查找已有 Negative Findings；
4. 查找历史 experiments；
5. 查找已有 conclusions；
6. 判断现有知识是否仍适用。

核心原则：

> **Research first. Avoid rediscovering known project knowledge.**

如果已有文档足够：

> SHOULD reuse / update，而不是创建重复文档。

---

# 3. Evidence First

DOCS 中的重要工程结论 SHOULD 有可追踪依据。

推荐 Evidence Priority：

```text id="f1m19b"
Runtime / Test
      ↓
Source
      ↓
Configuration
      ↓
Official Documentation
      ↓
Existing Project Documentation
      ↓
Inference
```

该顺序是默认 guidance，不是机械绝对排序。

Agent SHOULD 根据具体 claim 判断 Evidence strength。

---

# 4. Conclusion First

工程文档 SHOULD 优先使用：

```text id="mukjqw"
Conclusion
   ↓
Evidence
   ↓
Explanation
   ↓
Detail
```

而不是要求未来 Agent 阅读大量过程记录后自己寻找结论。

目标：

> **高信息密度和低检索成本。**

---

# 5. Knowledge State

DOCS MUST 区分：

### CONFIRMED

已有可靠 evidence 支持。

### INFERRED

基于 evidence 的合理推断，但没有直接验证。

### UNKNOWN

当前信息不足。

### PENDING_VALIDATION

已有具体 hypothesis / candidate，但仍需验证。

不得：

* 将 inference 写成 confirmed fact；
* 将 unknown 填成猜测；
* 将 research candidate 写成 engineering truth。

---

# 6. Unknown Is Valid

DOCS MAY 明确记录：

`UNKNOWN`

这是合法知识状态。

例如：

```text id="4c30xa"
Known:
- CPU pose values change.

Unknown:
- Whether this execution path updates GPU skinning.

Required validation:
- Render-side observable probe.
```

这种记录比编造完整解释更有价值。

---

# 7. Negative Findings

Negative Findings 是正式项目知识。

例如：

* 某 API 在特定版本不可用；
* 某 execution path 已验证无效；
* 某 workaround 不能解决 underlying correctness；
* 某历史假设已被 evidence 排除；
* 某 library combination 存在 incompatibility；
* 某方案在目标环境 NOT_FEASIBLE。

Agent SHOULD 保存具有未来复用价值的 Negative Findings。

目的：

> **避免未来 Agent 重复走已经证明无效的路径。**

---

# 8. Existing Knowledge Before New Knowledge

如果发现已有相关文档：

优先考虑：

```text id="lceo67"
Existing document
      ↓
Still correct?
     / \
   YES  NO
    ↓    ↓
Update  Correct / Supersede
```

MUST NOT 为同一个结论机械创建：

```text id="by18c9"
research-v2
research-final
research-new
research-latest
research-final-2
```

除非这些文档确实代表不同历史阶段且具有保留价值。

---

# 9. Conflict Handling

当多个 DOCS 来源发生冲突：

Agent MUST NOT 静默任选一个。

SHOULD：

1. Identify conflict；
2. Compare evidence；
3. Compare applicable environment/version；
4. Determine freshness；
5. Determine authority；
6. Resolve when evidence allows；
7. Otherwise explicitly preserve uncertainty。

如果旧知识已经失效：

SHOULD：

* update；
* mark stale；
* supersede；
* archive；

而不是让冲突长期保持隐形。

---

# 10. Freshness

对可能随时间变化的知识 SHOULD 标记适用条件。

例如：

* product version；
* engine version；
* library version；
* date；
* platform；
* execution mode；
* configuration。

例如：

```text id="vqgwbo"
Applies to:
- Unreal Engine 5.8
- UnrealEditor-Cmd
- verified 2026-09-22
```

不要把特定版本事实写成永久普遍事实。

Knowledge state 与 lifecycle MUST 独立：

| Dimension | Values |
|---|---|
| Knowledge state | `CONFIRMED`、`INFERRED`、`UNKNOWN`、`PENDING_VALIDATION` |
| Lifecycle | `ACTIVE`、`STALE`、`SUPERSEDED`、`HISTORICAL` |

`CONFIRMED + HISTORICAL` 表示结论在原适用条件下已确认，但不代表当前入口。MUST NOT 通过降低 knowledge state 来表达 freshness 或 supersession。

---

# 11. Traceability

重要结论 SHOULD 能追溯到：

* runtime evidence；
* test；
* source；
* configuration；
* official documentation；
* experiment；
* OpenSpec；
* FEV result；
* other durable evidence。

目标不是每句话都加 citation。

目标是：

> **关键工程 claim 能够被重新检查。**

---

# 12. Experiment Documentation

如果 DOCS 保存实验，应尽量包含：

```text id="e9rxdp"
Environment
    ↓
Setup
    ↓
Action
    ↓
Observation
    ↓
Conclusion
```

必要时增加：

* Hypothesis；
* Acceptance criteria；
* Raw evidence；
* limitations；
* reproduction instructions。

不要只保存：

> “试过，不行。”

---

# 13. Reproducibility

对于未来可能需要重新验证的知识，SHOULD 保存足够信息使 Agent 能重建结论。

包括必要时：

* commands；
* versions；
* assets；
* configuration；
* inputs；
* thresholds；
* output；
* screenshots；
* logs；
* expected behavior。

但：

> **Reproducibility ≠ 保存所有噪声。**

---

# 14. Technical Relationships

复杂技术关系 SHOULD 优先使用结构化表达。

适合使用：

* Mermaid；
* table；
* state diagram；
* sequence diagram；
* dependency graph；
* flowchart。

对于 design-related DOCS：

> SHOULD normally include at least one Mermaid diagram when a diagram materially improves understanding.

不得为了满足格式机械生成无信息价值图表。

---

# 15. Tables

以下信息 SHOULD 优先使用 table：

* comparisons；
* state matrices；
* version differences；
* API behavior；
* acceptance results；
* experiment matrix；
* configuration differences；
* known / unknown；
* option trade-offs。

目标：

> **提高 Agent 扫描和检索效率。**

---

# 16. Information Density

DOCS SHOULD 优先记录：

* non-obvious behavior；
* hidden dependency；
* lifecycle；
* data flow；
* runtime behavior；
* edge conditions；
* failure mode；
* validation method；
* excluded solutions；
* important constraints；
* difficult-to-rediscover facts。

SHOULD avoid：

* 重复源码本身；
* 显而易见的信息；
* 大量低价值过程日志；
* 无结论的聊天转储；
* 为文档数量而文档化。

---

# 17. Agent Conversation Knowledge

Agent conversation MAY 成为知识来源。

但 SHOULD：

```text id="b7gx90"
Conversation
    ↓
Synthesis
    ↓
Durable Knowledge
    ↓
DOCS
```

而不是：

```text id="oxv54g"
Conversation dump
      ↓
DOCS
```

应提取：

* decisions；
* verified conclusions；
* important reasoning outcome；
* constraints；
* rejected approaches；
* unresolved questions。

避免保存大量无长期价值对话噪声。

`SESSION_SNAPSHOT` 是合法 DOCS 类型，用于恢复当次 Human–Agent context，但不自动成为 verified fact。长期有效内容 SHOULD 从 Session Snapshot 提炼到 Topic Summary、Decision、Negative Finding、Evaluation 或 Evidence Analysis。

当用户引用 Topic directory 时，Agent SHOULD 先读唯一 Topic Summary，再按任务逐层展开 supporting files；MUST NOT 因目录被引用就默认加载全部历史 Session Snapshot。

---
# 17A. Topic and Document Roles

Topic 是 reusable knowledge 的主要聚合单位。常见 document role 包括：

* `TOPIC_SUMMARY`；
* `SESSION_SNAPSHOT`；
* `PIPELINE_DESIGN`；
* `DECISION`；
* `NEGATIVE_FINDING`；
* `EVALUATION`；
* `EVIDENCE_ANALYSIS`；
* `REFERENCE`。

Topic Summary SHOULD 保存当前结论、state、lifecycle、applicability、authority、关键 Evidence 与 supporting links，并作为 directory reference 的低 Token cost 入口。Domain MAY 作为多值 metadata 或 collection view；不得因单一物理分类而复制跨域 Topic。

---
# 17B. Pipeline Design and Evidence Analysis

DOCS MAY 保存 Pipeline candidate design、Decision 与 intended behavior。Design 经 Human 确认并 handoff 后，Pipeline Graph、script、contract、Acceptance 与 Run 成为 actual behavior authority；DOCS MUST NOT 保留第二套现行 Pipeline contract。

DOCS MAY 分析 Pipeline Run，并保存 cross-run synthesis 与 Negative Finding。`EVIDENCE_ANALYSIS` SHOULD 区分 Observation、Interpretation、Conclusion、Unknown 与 Limitations，并引用 stable Run identity。复制 Run output 到 DOCS 不改变 Evidence authority。

Pipeline PASS 不自动产生 business change。Agent MAY 给出 Promotion Recommendation；只有 Human 明确确认 `APPROVED` 后，才进入 OpenSpec。OpenSpec owns normative `SHALL`、scenarios、scope 与 tasks。

---

# 18. Out-of-Scope Findings

Agent 在工作中发现额外问题时：

```text
Finding
  ↓
Required for current task?
  ├─ YES → current work
  └─ NO  → do not create backlog; record only through a separately authorized formal workflow
```

不要因为 DOCS 存在就记录所有发现，也不得建立替代 backlog mechanism。

---

# 19. Sensitive Information

DOCS MUST NOT 保存：

* passwords；
* tokens；
* API secrets；
* private keys；
* credentials；
* unnecessary PII；
* sensitive environment secrets。

示例和配置 MUST 使用安全 placeholder。

---

# 20. Links and References

项目内部引用 SHOULD 优先使用：

`relative links`

Agent SHOULD：

* 避免无效链接；
* 修改文件位置时修复相关链接；
* 引用 authoritative source；
* 避免无必要复制完整内容。

如果知识已有明确 source：

> Prefer reference + synthesis over blind duplication.

---

# 21. Authority and Handoff

DOCS consumes reusable knowledge without taking over the producer's authority:

| Producer / owner | DOCS MAY preserve | DOCS MUST NOT do |
|---|---|---|
| BMAD | Research Candidate、comparison、decision context | 把 Candidate 写成 verified fact |
| FEV | experiment context、Root FEV reference、durable finding、Evidence link、Negative Finding、Verdict / Aggregate Verdict reference | 签发或覆盖 FEV Verdict；orchestrate Investigation Tree / Sub-FEV Parent-Child relationship |
| ICD | Acceptance design、Evidence link、Result reference | 决定 Capability PASS |
| CED | reusable blocker analysis、lesson、completion report reference | 成为 authoritative Epic state store |
| OpenSpec | explanation、rationale、cross-reference | 替代 normative SHALL / change record |

Handoff MUST preserve source、knowledge state、authority 与 freshness。复制到 DOCS 不提升 claim strength，也不改变 producer-owned status。CED 的 authoritative report 应与 Epic 的 OpenSpec / project engineering trace 共址或由其明确链接。

---
# 22. DOCS Is Not a Second Implementation

DOCS MUST NOT 成为：

* source-code mirror；
* hidden configuration system；
* executable policy substitute；
* duplicate implementation；
* second OpenSpec；
* second issue tracker；
* second Epic tracker。

Documentation MAY explain implementation。

Implementation truth 最终仍由：

* code；
* runtime；
* tests；
* authoritative engineering system；

决定。

---

# 23. Suggested Research Layout

对于新的独立 Research，当前推荐：

```text id="ctbpkd"
docs/
└── <YYYY-MM-DD>-<topic>/
    ├── 00-调研总览.md
    ├── 01-...
    ├── 02-...
    └── ...
```

`00-调研总览.md` SHOULD 优先提供：

* Conclusion；
* Scope；
* Key Evidence；
* Known / Unknown；
* Important Constraints；
* Links to detail。

但这是：

`SHOULD`

而不是所有 DOCS 内容的强制目录结构。

如果项目已有更成熟 convention：

> Prefer existing compatible convention.

---

# 24. PENDING Knowledge Governance

Retrieval、cross-source semantic conflict resolution、freshness judgment 与 lifecycle maturity 仍是 `v0.10.0` 的 PENDING areas。当前已定义 Topic-first read behavior、state / lifecycle separation、Pipeline Evidence Analysis 与 Human Promotion boundary，但不定义自动 RAG、完整 Authority Engine 或自动 semantic truth judgment。

在这些机制成熟前，Agent SHOULD 保证 naming、topic、summary 与 link 可检索；识别原始 evidence 和更明确的 owner；检查 applicability 与 freshness；优先更强证据；对冲突、stale 或 superseded knowledge 显式标记。新 evidence 使旧知识失效时，更新、标记 stale、supersede 或 archive，而不是静默并存。

这些未完全形式化的领域不阻止 DOCS 使用，也不构成 maturity promotion。项目 SHOULD 通过真实使用积累 evidence。

---
# 25. Agent Read Behavior

当任务涉及已有项目领域知识时，Agent SHOULD：

```text id="45c36f"
1. Discover relevant DOCS
        ↓
2. Read summaries / conclusions
        ↓
3. Check applicability
        ↓
4. Check evidence / authority
        ↓
5. Check freshness
        ↓
6. Reuse valid knowledge
        ↓
7. Validate when uncertainty matters
        ↓
8. Update knowledge if reality changed
```

Agent MUST NOT：

> 因为 DOCS 中写过，就无条件视为当前事实。

---

# 26. Agent Write Behavior

当产生新知识时：

```text id="mblp3v"
1. Is it valuable beyond current execution?
        ↓
2. Does it have a clearer owner?
        ↓
3. Does related DOCS already exist?
        ↓
4. Update rather than duplicate when possible
        ↓
5. State conclusion
        ↓
6. Attach evidence / trace
        ↓
7. Mark fact / inference / unknown
        ↓
8. Record applicability / version when volatile
        ↓
9. Link related knowledge
```

---

# 27. Anti-Patterns

Agent MUST NOT：

* 把 DOCS 当普通杂物目录；
* 为所有知识定义严格内容白名单；
* 因内容类型“不标准”拒绝有价值知识；
* 抢占 OpenSpec / FEV / ICD / CED authority；
* 把 BMAD Candidate 写成 verified fact；
* 把 inference 写成 confirmed fact；
* 把 UNKNOWN 填成猜测；
* 重复创建已经存在的 Research；
* 保留明显冲突却不标记；
* 将旧版本事实写成永久事实；
* 保存 secrets；
* 保存大量无价值 conversation dump；
* 创建第二套 implementation；
* 为了“知识完整”记录所有噪声；
* 假装当前 v0.10.0 已解决所有 Retrieval / Authority / Freshness 问题。

---
