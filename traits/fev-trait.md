# FEV — Feasibility Engineering & Validation

## Metadata

```yaml
trait:
  id: fev
  version: "1.2.0"
  date: "2026-10-15"
  status: "Proposed"
  type: "Engineering Method"
  source_version: "1.1.0"
```

**补充：** 2026-10-15 — 明确 Run report、取消默认人工批阅、合并重复结果、Artifact Value / Retention 与历史材料边界（§33–§35）。
**修订：** 2026-10-15 — `1.2.0` 增加 Parallel Feasibility Investigation（同仓无 Worktree 的并发 Sub-FEV、write ownership、resource lease、evidence provenance、Root aggregation）。  
**修订：** 2026-09-26 — `1.1.0` 增加 Hierarchical Feasibility Investigation（Root / Sub-FEV / Aggregate Verdict、Uncertainty Decomposition、FEV↔DOCS boundary）。  
历史版本由来源仓 archive 保存；portable package 不复制历史材料。
Coordinator / lease runtime：[`../pipelines/_shared/fev_parallel/`](../pipelines/_shared/fev_parallel/)。

## Core Philosophy

**先验证方案可行性，再进入业务实现；用证据消除方案不确定性。**

对并行调查，额外保持：

> **Parallelize independent uncertainty reduction, not uncontrolled concurrent modification.**

Evidence integrity 与正确 feasibility verdict 优先于名义上的 Agent 并发。

FEV 的目的不是提前实现业务功能，而是在存在重要技术不确定性时，通过最小、针对性的工程实验回答：

> **这个 proposed solution 在目标环境中是否真的可行？**

FEV MUST distinguish：

`researched / plausible`

from：

`verified feasible`

研究资料、文档、源码阅读和已有经验可以形成 hypothesis，但不能单独证明目标环境中的实际可行性。

FEV 仍然是 **Risk Gate**，不是：

* mandatory ceremony；
* implementation framework；
* project manager；
* task tracker；
* knowledge base；
* documentation system；
* capability acceptance system。

---

# 1. Purpose

FEV 用于在业务实现前降低方案风险。

基本过程：

`Unknown → Hypothesis → Experiment → Evidence → Verdict → Implementation Guidance`

复杂 feasibility problem 还可形成 Investigation Tree：

`Root FEV → Experiment / Sub-FEV → Local Verdict → Parent Evidence → Aggregate Verdict`

FEV SHOULD 将方案不确定性转换为：

* verified facts；
* evidence；
* constraints；
* failure modes；
* negative findings；
* implementation guidance；
* unresolved unknowns。

FEV 的主要交付物不是 production implementation，而是：

> **可行性结论及其证据。**

---

# 2. Risk Gate

FEV MUST NOT 对所有任务机械执行。

只有存在值得验证的重要不确定性时，才 SHOULD / MUST 进入 FEV。

典型触发条件：

* 未知 framework / engine runtime behavior；
* 关键 API 行为不明确；
* documentation 与实际 runtime 可能不同；
* 多个候选技术方案且选择风险较高；
* 跨系统 / 跨引擎 / 跨坐标系 / 跨数据模型转换；
* 关键算法或 solver 行为存在不确定性；
* acceptance 依赖无法从静态代码可靠推导的 runtime behavior；
* 已出现与理论预期不一致的实际行为；
* 错误方案一旦进入业务实现，返工成本明显较高。

低风险、成熟、已经在当前目标环境充分验证的工作 MAY bypass FEV。

**FEV 是 Risk Gate，不是固定 ceremony。**

---

# 3. Pipeline as Experimental Carrier

Pipeline SHOULD 作为 FEV 的主要实验执行载体。

但必须保持：

```text
Pipeline ≠ FEV

FEV Pipeline ≠ Business Pipeline
```

Pipeline 只是组织、执行和复现实验的一种载体。

FEV MAY 使用：

* probe；
* harness；
* mock；
* minimal reproduction；
* experimental code；
* runtime measurement；
* readback；
* screenshot；
* logs；
* assertions；
* comparison scripts；
* temporary assets；
* controlled test scenes；
* other evidence-producing mechanisms。

选择实验载体的标准是：

> **能否以最低合理成本产生足以回答 feasibility question 的可靠证据。**

---

# 4. Experimental Code Boundary

FEV experimental code 默认：

**NOT production code**

除非后续工程阶段明确决定采用。

Agent MUST NOT 因为 probe “已经能工作”就自动：

* 将其视为 production implementation；
* 扩展为正式 architecture；
* 把实验 shortcut 固化为业务设计；
* 将测试 workaround 当作产品行为。

FEV 回答：

> **Can this work?**

后续工程阶段回答：

> **How should this be implemented and delivered correctly?**

---

# 5. Experiment Design

每个重要 FEV 实验 SHOULD 明确以下内容。

### Question

究竟要消除哪个 uncertainty？

### Hypothesis

当前认为可能成立的解释或方案是什么？

### Environment

在哪个实际目标环境中验证？

必要时记录：

* product / engine version；
* OS；
* runtime mode；
* relevant configuration；
* asset / dataset；
* execution path。

### Procedure

最小验证步骤是什么？

### Observable Evidence

什么结果可以被实际观察、读取或测量？

### Discrimination Criteria

什么 evidence 支持 hypothesis？

什么 evidence 否定 hypothesis？

### Result

实际观察到了什么？

### Verdict

根据 evidence 得出什么 feasibility conclusion？

---

# 6. Evidence Hierarchy

FEV SHOULD 优先使用能够直接观察目标行为的证据。

通常：

```text
Runtime / Test Evidence
        ↓
Source / Configuration Evidence
        ↓
Documentation
        ↓
Inference / Assumption
```

但 evidence strength MUST 根据具体问题判断。

Agent MUST NOT：

* 用 documentation claim 替代 runtime verification；
* 用“代码看起来正确”替代实际 behavior；
* 用 screenshot 印象替代已有数值 readback；
* 用单一视觉结果覆盖更强的 instrumentation evidence；
* 将 inference 写成 verified fact。

---

# 7. Fact / Hypothesis / Unknown

FEV MUST 区分：

### VERIFIED

已经有足够 evidence 支持。

### HYPOTHESIS

存在合理解释，但尚未被验证。

### UNKNOWN

当前 evidence 不足以判断。

UNKNOWN 是合法工程结果。

Agent MUST NOT 为了完成任务而把 UNKNOWN 自动升级为 VERIFIED。

---

# 8. Negative Findings

Negative Finding 是 FEV 的正式产物。

例如：

* 某 API 在目标 execution mode 下不会产生预期行为；
* 某方案只修改 CPU state，但不会影响 renderer；
* 某 execution path 无法 flush 到目标 runtime state；
* 某 workaround 只能改善 presentation，不能修复 solver correctness；
* 某方案在目标版本中不存在；
* 某路径理论成立但实际目标环境不可用。

Agent SHOULD 保存能够避免未来重复踩坑的 Negative Findings。

---

# 9. Verdict

FEV 最终 Verdict MUST 使用以下语义之一。

### FEASIBLE

已有足够 evidence 证明 proposed solution 在目标环境满足当前 feasibility question。

### NOT_FEASIBLE

已有足够 evidence 证明 proposed solution 在当前约束下不可行。

### PARTIALLY_FEASIBLE

方案只有部分能力被证明可行，仍存在明确限制。

### BLOCKED

验证无法继续，因为存在外部 blocker，且当前无法取得必要 evidence。

### INCONCLUSIVE

已经执行验证，但现有 evidence 不足以支持 `FEASIBLE` 或 `NOT_FEASIBLE`。

核心约束：

> **INCONCLUSIVE MUST NOT be treated as FEASIBLE.**

在 Investigation Tree 中：

* Sub-FEV owns **Local Verdict**（scope = 当前 Sub-FEV Question）；
* Root FEV owns **Aggregate Verdict**（scope = Root Question）。

Local Verdict MUST NOT 默认传播为 Aggregate Verdict。详见 §19–§21。

---

# 10. Evidence Before Verdict

Agent MUST NOT 先决定 Verdict，再寻找支持材料。

正确方向：

```text
Question
   ↓
Experiment
   ↓
Evidence
   ↓
Interpretation
   ↓
Verdict
```

禁止：

```text
Desired Verdict
      ↓
Select Supporting Evidence
```

当 evidence 与原 hypothesis 冲突时：

> **更新 hypothesis，而不是解释掉 evidence。**

---

# 11. Failure Localization

当复杂系统失败时，FEV SHOULD 尽可能分层定位，而不是直接对最终视觉结果猜测根因。

例如：

```text
Input Correct?
      ↓
Transform / State Correct?
      ↓
Solver Correct?
      ↓
Writeback Correct?
      ↓
Runtime Application Correct?
      ↓
Rendering / Presentation Correct?
```

具体层级根据 domain 定义。

核心原则：

> **上游已经有 evidence 证明正确的层，不应在没有新反证时重新作为默认根因。**

Agent SHOULD 优先定位第一个 evidence failure boundary。

当 failure localization 产生新的、可独立验证且能影响 Parent reasoning 的 feasibility question 时，MAY 进入 Hierarchical Feasibility Investigation（§18+），而不是把所有局部问题压成无结构的长实验记录。

---

# 12. No Presentation Fix as Solver Proof

视觉改善不等于工程正确。

如果某 workaround：

* clamp；
* smoothing；
* damping；
* interpolation；
* hiding；
* presentation offset；
* post-process correction；

只是让结果“看起来更好”，它 MUST NOT 被描述为 underlying solver / state / transformation correctness 的修复，除非 evidence 证明其确实解决对应问题。

Presentation strategy MAY 合法存在，但必须：

* 明确命名；
* 明确所属层；
* 与 solver / state correctness 分离。

---

# 13. Reproducibility

关键 feasibility Verdict SHOULD 可以被未来 Agent 或人重新验证。

Evidence artifact SHOULD 在合理情况下记录：

* environment；
* input；
* command / execution method；
* relevant configuration；
* observed values；
* expected values；
* thresholds；
* logs；
* screenshots；
* output artifacts；
* reproduction limitations。

不要为了形式完整制造大量无价值 artifact。

原则：

> **保留足够重建结论的 evidence，而不是保存所有过程噪声。**

---

# 14. Scope Control

FEV MUST 回答当前 feasibility question。

实验过程中发现的独立问题：

### Directly affects Verdict

当前处理；必要时作为 Sub-FEV（Uncertainty Decomposition），而不是无限拉长 Parent experiment。

### Does not affect Verdict but has future value

记录；若有独立 engineering value 且不应阻塞 Parent，MAY Promote / Spawn Independent FEV（§24），或写入 DOCS durable knowledge / future investigation record。

### Unrelated

不扩展当前 FEV scope。

FEV MUST NOT 因发现新的工程问题而无限扩大实验范围。

---

# 15. Authority and Handoff

FEV owns feasibility questions、Investigation Tree、target-environment evidence、Local Verdict 与 Aggregate Verdict。它 MAY consume BMAD candidates and project facts, but MUST independently validate any critical unknown.

| Related system | Boundary |
|---|---|
| BMAD | supplies candidates and research; MUST NOT override FEV Verdict |
| ICD | consumes feasibility evidence when relevant, then independently judges Capability Acceptance |
| CED | consumes Verdict as execution evidence and decides continue、defer or legal stop |
| DOCS | MAY preserve experiment context、Root FEV reference、durable finding、Evidence link、Negative Finding and Verdict / Aggregate Verdict reference; MUST NOT issue a Verdict; MUST NOT orchestrate Investigation Tree / Sub-FEV Parent-Child relationship |

`FEASIBLE` does not imply ICD PASS or Epic completion. `NOT_FEASIBLE` does not by itself select CED STOP. When the Risk Gate does not trigger, work MAY proceed without a separate FEV stage.

**Active Feasibility Investigation Structure belongs to FEV.**

包括：Question、Hypothesis、Experiment、Investigation Tree、Sub-FEV、Nested Sub-FEV、active evidence、Local Verdict、Aggregate Verdict、escalation / origin relationship。

DOCS 负责 Durable / Reusable Project Knowledge，不负责 orchestrate Sub-FEV。

反方向同样禁止：FEV MUST NOT 因为支持 Investigation Tree 就保存无关 domain knowledge、historical documentation、general API references 或 long-term project lessons。判断：

```text
Needed to resolve active feasibility question?
        ├─ YES → FEV
        └─ NO
             ↓
Reusable durable knowledge?
        ├─ YES → DOCS
        └─ NO → do not preserve
```

---

# 16. Agent Default Behavior

当 Agent 面临重要技术不确定性时：

```text
1. Identify uncertainty
        ↓
2. Evaluate Risk Gate
        ↓
3. Define smallest useful feasibility question (Root or Sub-FEV)
        ↓
4. Inspect existing evidence / Parent inherited context
        ↓
5. Form hypothesis
        ↓
6. Design minimum discriminating experiment
        ↓
7. Execute in target environment
        ↓
8. Collect observable evidence
        ↓
9. Separate VERIFIED / HYPOTHESIS / UNKNOWN
        ↓
10. If new independently testable uncertainty appears → Sub-FEV Creation Gate (§20)
        ↓
11. Produce Local Verdict (Sub-FEV) or Aggregate Verdict (Root)
        ↓
12. Integrate Sub-FEV impact into Parent (§22)
        ↓
13. Record constraints / Negative Findings
        ↓
14. Produce implementation guidance
        ↓
15. End FEV when question is sufficiently answered;
    Promote Independent FEV or hand durable findings to DOCS when appropriate
```

---

# 17. Reasonable Experiment / Investigation Principle

FEV SHOULD continue experimentation while an additional experiment:

* can materially discriminate between competing hypotheses；
* can produce new relevant evidence；
* can materially change the Verdict；
* or can resolve an important UNKNOWN。

对 Investigation Tree，继续 Experiment / Sub-FEV 的前提至少还包括：

* 能实质缩小 Parent uncertainty；
* 结果能改变、收缩或解释 Parent reasoning；
* 单纯继续 Parent experiment 会显著降低 clarity。

FEV SHOULD stop adding experiments / Sub-FEV when additional work is unlikely to change the engineering conclusion。

Do not use arbitrary rules such as:

`always retry N times`

或

`max_sub_fev_depth = N`

unless the project/domain explicitly requires them。

继续拆分的判断是：是否仍然产生新的 discriminating evidence，并实质缩小 Parent uncertainty。如果进一步拆分不再产生新 evidence、只是重新命名同一问题、只是普通 debugging、或无法改变 Parent reasoning，则 SHOULD 停止 decomposition。

---

# 18. Hierarchical Feasibility Investigation

FEV MUST 支持 Investigation Tree，用于复杂 feasibility problem 在调查中不断产生新的局部 uncertainty / failure scope 的情况。

基本结构：

```text
Root FEV
│
├── Question
├── Scope
├── Environment
├── Constraints
├── Evidence
│
├── Sub-FEV A
│   ├── Local Question
│   ├── Experiment
│   ├── Evidence
│   └── Local Verdict
│
├── Sub-FEV B
│   ├── Local Question
│   │
│   └── Nested Sub-FEV B.1
│       ├── Experiment
│       ├── Evidence
│       └── Local Verdict
│
└── Aggregate Verdict
```

Root FEV 是整个 feasibility investigation 的 authority boundary。

不得把每个派生问题都建成 Independent FEV，以免：

* duplicated context；
* evidence fragmentation；
* Parent/Child relationship 丢失；
* Local Verdict 与 Aggregate Verdict 混淆；
* DOCS 被迫承担 FEV relationship orchestration。

---

# 19. Root FEV / Sub-FEV / Nested Sub-FEV

### Root FEV

Root FEV 表示当前需要解决的最高层 feasibility question。

Root FEV SHOULD 定义：

* Root Question；
* Scope；
* Target Environment；
* Important Constraints；
* discrimination criteria；
* Known Evidence；
* Known Unknowns；
* applicable Negative Findings。

Root FEV MAY：直接运行 Experiment；派生 Sub-FEV；聚合 Sub-FEV evidence；更新 hypothesis；收缩 uncertainty；最终产生 Aggregate Verdict。

### Sub-FEV

Sub-FEV 是 Parent FEV 为缩小 uncertainty / failure scope 而派生的局部 feasibility investigation。

Sub-FEV MUST NOT 被理解为：普通 Task、implementation task、arbitrary work breakdown、documentation section、independent project、或 retry record。

Sub-FEV 的目的必须是：

> 回答一个可以独立验证、并且其答案能够影响 Parent FEV reasoning 的 feasibility question。

### Nested Sub-FEV

Sub-FEV MAY 继续产生 Sub-FEV。这仍然属于同一个 Root Feasibility Investigation。

Nested Sub-FEV SHOULD 只在新的 Uncertainty Decomposition 确实提高调查清晰度时创建。不得为了目录整齐而无限递归拆分。

---

# 20. Uncertainty Decomposition and Creation Gate

Sub-FEV decomposition 是 **Uncertainty Decomposition**，不是 Task Decomposition。

推荐判断：

```text
Experiment FAIL / UNKNOWN
          ↓
Cause already sufficiently known?
       ┌──┴──┐
      YES    NO
       │      │
       │      ▼
       │   Is there an independently
       │   testable feasibility question
       │   that can reduce Parent uncertainty?
       │        ┌────┴────┐
       │       YES        NO
       │        │          │
       ▼        ▼          ▼
    Record    Sub-FEV   Parent remains
    Evidence             BLOCKED /
                         INCONCLUSIVE
```

Agent SHOULD create a Sub-FEV only when all relevant conditions hold：

1. 当前 Parent FEV 出现新的 uncertainty / failure scope；
2. 该问题可以形成独立 feasibility question；
3. 可以设计有区分力的 experiment / evidence；
4. 结果能够改变、收缩或解释 Parent uncertainty；
5. 单纯继续 Parent experiment 会显著降低 clarity。

Agent MUST NOT 因为一个 test failed、command failed、implementation bug、普通 debugging、或需要多执行几个步骤，就机械创建 Sub-FEV。

---

# 21. Context Inheritance, Evidence Scope, Verdict Aggregation

### Context Inheritance

Sub-FEV MUST 默认继承 Parent FEV 的 applicable context（Environment、target version、platform、configuration、terminology、constraints、applicable evidence、confirmed facts、applicable Negative Findings、relevant assumptions）。

因此 Sub-FEV SHOULD 使用 **Delta Declaration**，而不是重新复制整个 Parent FEV。

Inheritance is not blind copying。若 Sub-FEV 改变 environment、engine version、execution mode、asset、configuration 或 assumptions，MUST 显式声明 delta；MUST NOT 静默继承不再适用的 evidence。

### Evidence Scope

每条 evidence SHOULD 明确属于 Root、某个 Sub-FEV、或多个节点共享。

Sub-FEV evidence MAY 被 Parent 使用，但：

> Evidence reuse requires applicability.

不得因为 evidence 位于同一 Investigation Tree 中，就默认对所有节点成立。

### Local Verdict vs Aggregate Verdict

允许继续使用 §9 Verdict vocabulary。

规则：

```text
Sub-FEV Local Verdict
          ↓
       Evidence
          ↓
Returned to Parent
          ↓
Parent interpretation
          ↓
Aggregate Verdict
```

> **Sub-FEV owns Local Verdict.**
> **Parent / Root owns Aggregate Verdict.**

禁止默认传播：

```text
Sub-FEV = NOT_FEASIBLE  →  Parent = NOT_FEASIBLE
Sub-FEV = FEASIBLE      →  Parent = FEASIBLE
```

除非 Parent Question 本身逻辑上完全依赖该 Sub-FEV，且 evidence 足以证明不存在其他有效路径。Parent MUST 根据整个 investigation scope 聚合 evidence。

---

# 22. Parent Integration and Traceability

Sub-FEV 完成后，Parent SHOULD 至少记录：

```text
Sub-FEV:
  <id>

Question:
  <local question>

Verdict:
  <local verdict>

Impact on Parent:
  - hypothesis eliminated
  - path validated
  - path rejected
  - uncertainty reduced
  - new unknown discovered
  - no material impact
```

Parent 不需要复制完整 Sub-FEV evidence；SHOULD 引用 Sub-FEV。

每个 Sub-FEV SHOULD 可追踪：

```text
Root → Parent → Current Sub-FEV
```

最低关系：

```yaml
id: FEV-001.3.2
root_fev: FEV-001
parent_fev: FEV-001.3
```

具体文件名、目录结构和 ID scheme MAY 由项目 Local Policy 定义。FEV Trait MUST NOT 强制特定 filesystem layout、numeric ID、database 或 tool；FEV 定义的是 semantic relationship。

---

# 23. Recommended Lifecycle

复杂 feasibility investigation 推荐：

```text
DOCS Topic / Engineering Context
              │
              ▼
     Feasibility Question
              │
              ▼
          Root FEV
              │
      ┌───────┴────────┐
      ▼                ▼
  Experiment        Sub-FEV
                       │
                 ┌─────┴─────┐
                 ▼           ▼
            Experiment   Nested Sub-FEV
                 │           │
                 └─────┬─────┘
                       ▼
                 Local Verdict
                       │
                       ▼
                Parent Evidence
                       │
                       ▼
               Aggregate Verdict
                 ┌─────┴─────┐
                 ▼           ▼
          Implementation   Durable Findings
                 │           │
                 ▼           ▼
                ICD         DOCS
```

---

# 24. Escalation / Promotion to Independent FEV

调查过程中，Sub-FEV MAY 发现新问题。若该问题：

* 不再是解决 Parent Question 的必要组成部分；
* 有独立 engineering value；
* 有独立 scope；
* 后续 investigation 不应阻塞 Parent；

则 SHOULD **Promote / Spawn Independent FEV**，而不是无限扩展 Parent Investigation Tree。

推荐判断：

```text
New Question
     ↓
Required to resolve Parent?
   ┌────┴────┐
  YES        NO
   │          │
   ▼          ▼
Sub-FEV    Independent FEV
             │
             ▼
        preserve origin
```

由 Sub-FEV 派生出的 Independent FEV MUST 保留 origin relationship。例如：

```yaml
fev:
  id: FEV-017
  origin:
    parent_fev: FEV-001
    discovered_by: FEV-001.3.2
  relation:
    type: spawned-independent-investigation
```

目的：Independent ≠ Unrelated。

若问题只是“未来可能有价值”，但不需要现在验证：MAY 进入 DOCS durable knowledge / future investigation record；不得强制立即创建 Independent FEV。

---

# 25. Anti-Patterns

Agent MUST NOT：

* 对所有任务强制 FEV；
* 把互联网调研当 feasibility proof；
* 把源码阅读自动当 runtime proof；
* 为证明预设答案选择性收集 evidence；
* 把实验代码自动当 production code；
* 把视觉改善自动当 correctness；
* 把 `UNKNOWN` 当 VERIFIED；
* 把 `INCONCLUSIVE` 当 FEASIBLE；
* 在已有强 evidence 后无依据回退到已排除根因；
* 为了“完整”制造大量无价值实验；
* 让 FEV 无限扩大当前 task scope；
* 把 Sub-FEV 当普通 task breakdown / retry record；
* 因 test / command / bug 失败就机械创建 Sub-FEV；
* 默认将 Local Verdict 传播为 Aggregate Verdict；
* 用 DOCS 手动维护无关 FEV 列表来替代 Investigation Tree；
* 让 Investigation Tree 变成 knowledge base / documentation dump；
* 为目录整齐而无限 Nested Sub-FEV；
* 静默继承不再适用的 Parent evidence / execution-mode-specific facts；
* 在 write set / resource 冲突时仍强制并发；
* 假定 MCP 自带跨 Client locking；
* 用 prompt 约定替代 enforceable lease / ownership；
* 在 dirty working tree 上只靠 commit SHA 声明 provenance；
* 将 mock scheduler PASS 当作 live Editor/MCP operational support。

---

# 26. Parallel Feasibility Investigation

FEV 1.2.0 允许 Codex / Cursor 在 **同一 working repository、不强制 Git Worktree** 的前提下，对独立 Sub-FEV 并发调查。

MUST 保留 §18–§24 的 Hierarchical 语义：

1. Root FEV owns **Aggregate Verdict**。
2. Sub-FEV 是 independently testable uncertainty 的分解，不是 arbitrary task slice。
3. 每个 Sub-FEV 只 owns **Local Verdict** 与其 evidence。
4. Sub-FEV 继承 Parent environment / constraints / terminology / applicable evidence / Negative Findings；只声明 local delta。
5. Local `NOT_FEASIBLE` 不自动等于 Root `NOT_FEASIBLE`。
6. Verdict vocabulary 不变：`FEASIBLE` / `NOT_FEASIBLE` / `PARTIALLY_FEASIBLE` / `BLOCKED` / `INCONCLUSIVE`。
7. 不得 mutate historical evidence，也不得把 `INCONCLUSIVE` 升级为 `FEASIBLE`。

Out of scope：

* mandatory Git Worktree / branch-per-Agent；
* 同文件 concurrent edit 的 automatic semantic merge；
* 用 FEV 替换 CED / ICD；
* 假定 MCP 提供 built-in cross-client locking；
* 保证 headless 与 GUI Editor 完全 parity；
* mandatory third-party gateway / database / Docker / distributed cluster。

---

# 27. Concurrency Eligibility

Sub-FEV MAY 并发，仅当：

* 测试 separately falsifiable uncertainty；
* write set 不与另一 active Agent 的 write set 重叠；
* output path 与 `run_id` 唯一；
* resource 需求可 lease，或已证明 safely concurrent；
* 不依赖另一 Sub-FEV 未完成的 evidence，除非 dependency 已显式表示且已满足。

否则只 serialize 冲突 stage，不一定 serialize 整个 Sub-FEV。Read-only source inspection 与独立 reasoning MAY 并行。

> **同一 shared repository ≠ 共享 write permission。**

---

# 28. Ownership and Filesystem Layout

本仓默认落在既有 `pipelines/graphs/<domain>/<slug>/` 约定上。Illustrative layout：

```text
pipelines/graphs/<domain>/<root-slug>/
  root-fev.md                 # orchestrator only
  sub-fev/
    <sub-a>/                 # Agent A write owner
      investigation.md
      probes/
      runs/<run-id>/         # immutable after finalization
    <sub-b>/                 # Agent B write owner
      investigation.md
      probes/
      runs/<run-id>/
  aggregate/                 # orchestrator only
    report.md                # Aggregate Verdict + reasoning + Evidence links
    evidence-index.json
```

上例用于说明 ownership，不要求机械创建每个文件。Aggregate Verdict MAY 写在 Root report 中；仅当有独立 consumer / authority 需求时另建 carrier，不重复维护同一结论。Artifact 取舍遵循 §34。

Ownership rules：

* 每个 worker 有声明的 `write_scope`；其余 path 视为 read-only。
* Root metadata、shared traits、shared harnesses、dependency manifests、integration files 只能有一个 designated writer，或另需 exclusive lease。
* 即使改不同行，也不得并发 edit 同一文件。
* temporary output、log、screenshot、build dir、cache、artifact name 在可行时 MUST 按 run 唯一。
* shared project file（`.uproject`、`.uasset`、`.umap`、`.blend`、C++ source、generated build file）需要 explicit ownership 与 runtime isolation。
* Agent prompt 不是 security boundary：coordinator MUST 检测 unauthorized change 并拒绝 integration。
* MUST NOT 自动 reset / checkout / cleanup / overwrite 另一 Agent 的 uncommitted change；MUST NOT 用 `git reset --hard` 或 destructive cleanup 作为冲突解决捷径。

本仓最小可执行实现位于 `pipelines/_shared/fev_parallel/`（host-evidence dialect）。

---

# 29. Resource Scheduler and MCP Serialization

Protected resource（如 `ue58_editor:<id>`、`blender_editor:<id>`、`ue58_build:<project>`、`gpu_heavy:<device>`）MUST 有单一 authority。

Mandatory behavior：

1. 对 protected Editor 的访问 MUST 经过同一 gateway / worker / enforceable lease boundary；不得 bypass 到 raw MCP endpoint。
2. `tool` lease 覆盖一次 atomic MCP operation；`transaction` lease 覆盖完整 stateful experiment（setup → simulation → readback → screenshot → evidence → restore/release）。
3. lease record MUST 含 `lease_id`、`resource_id`、`owner_agent`、`root_fev`、`sub_fev`、`run_id`、`acquired_at`、`expires_at`、`heartbeat`、`state`、`fencing_token`。
4. 支持 bounded wait、FIFO 或 documented fair scheduling、cancellation、timeout、heartbeat。
5. 用 fencing / worker-side token check 阻止 stale owner 在 lease expiry 后继续执行。
6. timeout 或 worker 死亡后，resource 进 `DIRTY` / `RECOVERING`；验证终止、state reset、health 后才能再发放 lease。
7. lock acquisition MUST 跨进程 atomic；plain unchecked marker file / prompt convention 不够。
8. 多 resource 获取 MUST 有 deterministic order，避免 deadlock；不得在等待另一 resource 时无限持有当前 resource。
9. Editor launch / shutdown / restart、DLL compile、project mutation、修改 protected state 的 external script，同属 coordination boundary。
10. UE 与 Blender resource lock 相互独立。Read-only command 仅在目标 integration 证明 side-effect-free 时才可并发。

单机 Windows 初始实现：local coordinator + durable state store + **每个 Editor 单一 owner process** 即可。ContextForge 等 gateway 可选。若 MCP server 无法经 gateway 路由，则使用 exclusive Editor worker 作为唯一允许访问的进程。

UE 自动化另须遵守 [`aiagent-windows-session-isolation-trait.md`](./aiagent-windows-session-isolation-trait.md)。

---

# 30. Parallel Task Lifecycle

```text
PROPOSED → READY → RUNNING → WAITING_RESOURCE → RUNNING
  → EVIDENCE_READY → LOCAL_VERDICT → AGGREGATED
```

Terminal exceptional states：`BLOCKED`、`INCONCLUSIVE`、`CANCELLED`、`FAILED_EXECUTION`。

execution failure MUST NOT 与 feasibility `NOT_FEASIBLE` 混淆。

**Default Continue, Explicit Stop：** 一个 Sub-FEV 等待 resource 时，继续其他 eligible investigation。只在 unresolvable execution blocker 或 human decision 时停止；deferred blocker MUST 记录 reason、affected scope、evidence、revisit condition。不得为了吞吐绕过 safety / resource gate。

---

# 31. Parallel Evidence Provenance

每个 run MUST 产出 machine-readable manifest，至少包含：

* `root_fev` / `sub_fev` / `run_id` / `agent` / `fev_version`
* `git_revision` 与 `dirty_tree_snapshot`（单 dirty tree 时 commit SHA 不够）
* `environment` / `input_fingerprint`
* `resource_leases`
* `evidence[]`（path + sha256）
* `negative_findings`
* `local_verdict`

Evidence finalization 后保留 manifest 与 hash；correction 创建 new run 或显式 superseding record。Root aggregation MUST 校验 integrity、compatible environment、provenance、unresolved contradiction，然后才签发 Aggregate Verdict。

对 UE animation / rendering：numeric pose readback alone 不证明 rendered GPU skinning。对 Blender / UE physics：screenshot alone 不证明 solver correctness。Evidence MUST 匹配 precise claim。

---

# 32. Parallel Acceptance Gates

| Gate | PASS criterion |
|---|---|
| P0 Compatibility | FEV 1.0 / 1.1 verdict semantics unchanged |
| P1 Parallel investigation | Independent Sub-FEVs make overlapping progress |
| P2 File ownership | Overlapping write detected; unauthorized integration rejected |
| P3 Tool serialization | At most one protected operation per resource |
| P4 Transaction isolation | No foreign mutation during owned transaction |
| P5 Crash / timeout recovery | Stale owner fenced; health verified before reuse |
| P6 Resource independence | UE and Blender resources can progress concurrently |
| P7 Evidence provenance | Dirty-tree runs attributable by input/output/agent/env/hash |
| P8 Verdict aggregation | Incomplete / contradictory evidence ≠ Root `FEASIBLE` |
| P9 Live Editor validation | Real UE5.8 / Blender MCP queueing, isolation, recovery demonstrated |

P3–P5 require executable contention / failure-injection tests。P9 在真实 Editor 不可用时 MUST 记为 `BLOCKED` / `INCONCLUSIVE`，不得用 mock PASS 宣称 live operational support。

Validated 条件：independent Sub-FEVs 可证并发推进、shared stateful resource 可证 serialize、evidence 可归因、Root 能正确聚合 Local Verdict。Prefer smaller proven implementation over ambitious unverified framework。


# 33. Run Delivery and Report

FEV Run MUST 交付 machine-readable summary / manifest、`report.md` 与支持结论的 Evidence。FEV MUST NOT 默认生成 `acceptance.md`、要求用户逐个 Run 回复 pass/fail，或因用户未回复而把已得到的 Verdict 标成 pending。

Experiment criteria、threshold 与 expected behavior MUST 保留在 experiment / contract 中；取消人工批阅不取消判定条件。Agent 根据 Evidence 给出 Verdict；machine checks PASS 不自动等于 `FEASIBLE`。Execution failure 不自动等于 `NOT_FEASIBLE`。

`report.md` MUST 先汇总本次问题、实际执行范围、主要结果和 Local / Aggregate Verdict，再说明：

- Observation：关键 measurement、expected / observed values 与 Evidence reference；
- Interpretation：Evidence 如何支持结论，区分 VERIFIED / HYPOTHESIS / UNKNOWN；
- Limitations：适用 environment / input / configuration、未执行项、Negative Findings 与剩余 Unknown；
- Implementation Guidance：结论对下一步的影响；
- Reproduction：stable Run identity、command / configuration 与 machine-readable provenance reference。

Root report MUST 解释 Sub-FEV 对 Aggregate Verdict 的影响、未解决 dependency 与 contradiction；不得只列 Local Verdict。报告不得仅复制 JSON 或罗列 checks。失败、BLOCKED 与 INCONCLUSIVE Run 同样需要结果汇总；缺 Evidence 必须说明，不能以用户 pass 补足。

Report 的标题、Scope 与主要结果 MUST 来自本次 recorded request / actual execution，不得沿用另一 experiment 的名称或旧 baseline 结论。所有影响 Verdict 的阶段结果和关键 artifact MUST 可从 report 找到；多个 view / control 各有作用时，分别给出链接并说明观察目标。

Diagnostic / probe、negative control 与提前失败同样适用结果汇总要求。Run 已创建后，正常退出和可处理的 build / process / validation failure MUST 写明失败阶段、原因、已取得 Evidence 与未执行项；不要求失败路径伪造缺失产物。Process crash 或强制终止来不及生成 report 时，恢复后 MUST 记录 interrupted execution 并补充失败汇总，不得改写已 finalized Evidence。

Machine result MUST 区分 execution status、validation result 与 feasibility Verdict。Finalization MUST 在所需 validation 后进行；不得用 validation 前的 simulation PASS 代表最终结果。未完成时明确标为 incomplete；缺失 / 截断 Evidence 导致的 validation error 必须记录，不能保留看似完整的 PASS。

仅当问题依赖用户偏好或缺少必要用户输入时提出具体问题，并说明影响；这不是 per-run approval。最终产品的用户验收仍由 ICD / 业务 Graph 独立规定。历史 Run 保留，不为迁移改写或删除。

---

# 34. Artifact Value and Canonical Results

每个新增或继续维护的 Artifact SHOULD 至少有一个明确用途：支持当前 claim、作为 validator / downstream consumer 输入、帮助复现 / failure localization，或帮助用户理解本次结果。仅为模板完整而复制状态或结论的文件 SHOULD 取消或合并。

| 内容 | 默认保存方式 |
|---|---|
| Question、criteria、threshold、input semantics | Experiment / contract；不得因取消 acceptance 删除判定条件 |
| 本次 Observation、Interpretation、Verdict、Negative Findings、Limits、Guidance | 对应 scoped `report.md`；不默认拆成 verdict / feasibility / backlog / negative-findings 文件 |
| Checks、metrics、阶段结果 | 一个 canonical machine result；summary 可作为该 carrier |
| Run identity、environment、input / source fingerprints、lease、Evidence hashes | Manifest / provenance index；引用 canonical result 的 path / hash |
| Trace、readback、control、surface / topology cache、render output、必要 logs | 按具体 claim、consumer 与 reproduction 需要保留，并从 report 导航 |

Agent MUST NOT 将同一完整 audit / metrics 无区别复制到 `result.json`、`summary.json`、validation JSON 和 manifest，再把这些副本当作额外 Evidence。不同 carrier 确有独立 consumer / schema contract 时 MAY 保留，但 MUST 指定 canonical source，并通过派生生成和一致性校验避免状态分歧。Manifest 仍须满足 §31；必需 Verdict / provenance 字段不能因减少重复而丢失。

一个 Run 默认只有一个人读结果入口。Root / Sub-FEV 和不同实验 Scope 可以分别有 report，不能合成含糊的总 PASS。稳定 baseline MAY 保留 durable manifest 与指向具体 Run report 的链接；latest pointer 不替代 stable Run identity，也不成为另一份需要手工同步的结果正文。

Human approval 状态不得成为 FEV machine result 的必需字段。确需保留历史用户意见时，作为注明日期、Run 与 Scope 的 annotation；不得影响或替代 Evidence-based Verdict。

**用户不必阅读，不等于 Artifact 没有价值。** 不同 view、numeric trace 与 negative control 可以支持不同 claim；GIF / screenshot 也不自动替代 raw frames 或 solver readback。不得仅按文件名、文件数量或有无用户点击决定删除。

---

# 35. Active Material, History and Retention

Active contract 保存现行执行规则与 criteria；具体 Run 的结果、measurement 和限制进入 report。旧 solver、旧 Scope 或已被替代的 Decision / bootstrap 不得继续以未标注的 active authority 出现。

触达迁移时，Agent SHOULD 合并重复摘要、将旧版材料归历史，并更新引用、consumer 与 writer。仍有价值的 Negative Finding MUST 标明 experiment / Run、environment 与适用 Scope；不得把旧局部 `NOT_FEASIBLE` 写成当前全局结论。原始用户输入、重要 Decision 和失败 Evidence 有 provenance 价值时保留历史，不为减少 root 文件数量而销毁。

Artifact 精简 MUST 区分 future generation、active documentation 整理与 historical Evidence retention。规则更新不等于既有 Graph 已迁移；实际迁移必须同步 config、collector、writer、consumer 和合同，并验证引用 / 结果一致性。未迁移时明确说明。

Historical finalized Run 不回写、不删除。若既有 retention policy 允许清理 raw output，清理前 MUST 确认无 active validator / replay / downstream consumer 依赖，保留重建结论所需的 durable Evidence、manifest 与 hashes，并记录清理范围和 reproduction limitations。Derived preview 的存在本身不足以证明 raw Evidence 可清理；retention 不得静默降低 Verdict 的可验证性。
