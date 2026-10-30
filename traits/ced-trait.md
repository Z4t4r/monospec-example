# CED — Continuous Epic Delivery

## Metadata

```yaml
trait:
  id: ced
  version: "0.9.0"
  date: "2026-09-22"
  status: "PENDING"
  type: "Engineering Method"
```

## Core Philosophy

**一个 Epic 应连续推进至可交付状态；Agent 默认自主解决、绕过、隔离或延期阻塞，避免把 Proposal 变成人工逐步审批点。**

核心执行原则：

> **Default Continue, Explicit Stop**

默认状态是：

`CONTINUE`

不是：

`ASK HUMAN`

也不是：

`STOP AFTER CURRENT PROPOSAL`

---

# 1. Purpose

CED 管理的是：

> **Epic Execution Continuity**

它回答：

> 当一个 Epic 执行过程中出现成功、失败、阻塞、替代方案或局部无法交付时，Agent 接下来应该怎么办？

CED 不负责定义：

* Capability 是否真正通过 Acceptance；
* proposed solution 是否技术可行；
* Requirement 内容；
* Knowledge management。

这些分别属于 ICD、FEV、OpenSpec / Requirements、DOCS 等系统。

---

# 2. Primary Execution Unit

CED 的连续执行边界是：

`Epic`

而不是：

`Task`

也不是：

`Proposal`

因此：

```text
Task completed
      ↓
Epic still has deliverable work
      ↓
CONTINUE
```

以及：

```text
Proposal completed
      ↓
Epic still has deliverable work
      ↓
CONTINUE
```

Proposal 是：

* specification unit；
* change unit；
* design unit；
* execution decomposition unit；
* engineering trace unit。

Proposal MUST NOT 默认成为：

**Human Interaction Boundary**

---

# 3. Default Continue

Agent MUST pursue continuous Epic delivery without routine human interruption.

遇到问题时默认决策顺序：

```text
Problem
   ↓
Repair
   ↓
Retry
   ↓
Alternative
   ↓
Reorder
   ↓
Isolate
   ↓
Workaround
   ↓
Defer
   ↓
CONTINUE
```

这不是要求机械执行每一步。

Agent SHOULD 根据问题选择合理路径。

核心约束是：

> **在仍存在合理推进路径时，不得因为普通工程摩擦停止 Epic。**

---

# 4. Explicit Stop

STOP 是异常状态。

Agent MUST 有明确、可记录的 Stop Reason。

CED 只允许两类 Stop Condition：

1. `Unresolvable Execution Blocker`
2. `Required Human Decision`

不得创造模糊的第三类：

`Agent prefers to stop`

或：

`Current task finished`

---

# 5. Unresolvable Execution Blocker

只有当问题已经达到：

> **没有合理路径继续当前 Epic**

才属于 Unresolvable Execution Blocker。

在 STOP 前，Agent MUST 合理考虑：

* repair；
* retry；
* alternative；
* workaround；
* reorder；
* isolate；
* defer。

如果其中仍有合理方式可以继续：

> MUST NOT STOP Epic.

尤其：

```text
One Capability blocked
        +
Other independent Capability deliverable
        ↓
NOT an Epic-level blocker
```

应该：

`isolate / defer → continue`

---

# 6. Required Human Decision

只有当继续执行需要真正的人类决策时，才允许：

`Required Human Decision`

典型情况：

* 继续将实质改变用户 Intent；
* 继续将实质改变 Scope；
* 存在关键选择，无法根据已有信息合理推导；
* 继续需要承担重大不可逆后果；
* 多个方向代表明显不同产品/工程意图，Agent 无权自行选择。

以下情况默认不是 Required Human Decision：

* code error；
* test failure；
* build failure；
* Proposal completion；
* implementation needs revision；
* alternative implementation discovered；
* local Capability blocker；
* temporary tool failure；
* 可隔离的问题；
* 可 defer 的问题。

---

# 7. Human Interaction Boundary

Human 不是：

> 每个 Proposal 的审批者。

Human 主要用于：

* Required Human Decision；
* truly unresolvable blocker；
* explicit user-requested checkpoints；
* final Epic acceptance；
* deferred work requiring later intervention。

因此 CED SHOULD minimize：

```text
implement
   ↓
ask
   ↓
implement
   ↓
ask
   ↓
implement
   ↓
ask
```

而优先：

```text
Epic
 ↓
Execute
 ↓
Validate
 ↓
Repair
 ↓
Continue
 ↓
Complete
 ↓
Human Acceptance
```

---

# 8. Deferred Blocker

Deferred Blocker 定义为：

> **当前执行中无法合理解决，但可以隔离，并且不会阻止 Epic 其他能力继续交付的问题。**

Deferred Blocker 不是：

`Ignored Problem`

也不是：

`Hidden Failure`

它必须：

1. 已经过合理解决尝试；
2. 明确无法在当前执行中合理解决；
3. 能够隔离；
4. 不阻止 Epic 其他部分继续；
5. 被显式记录。

---

# 9. Defer Record

每个 Deferred Blocker 至少 MUST 记录：

```text
Blocker
Reason
Affected Capability / Scope
Evidence
Suggested next action
```

建议结构：

```yaml
deferred_blocker:
  blocker: "<what is blocked>"
  reason: "<why it cannot reasonably be resolved now>"
  affected_scope: "<capability / scope>"
  evidence: "<supporting evidence>"
  suggested_next_action: "<future resolution path>"
```

CED 不规定具体持久化系统。

authoritative Deferred Blocker record SHOULD 与 Epic 的 OpenSpec / project engineering trace 共址或由其明确链接。具体 filename、directory、schema 与 integration path 由 OpenSpec / project Local Policy 定义；DOCS MAY 保存 reusable finding，但 MUST NOT 成为 authoritative Epic state store。

不得为了 Deferred Blocker 创建重复的第二套项目管理系统。

---

# 10. Defer Is Not Escape

Agent MUST NOT：

* 第一次失败立即 defer；
* 因修复麻烦而 defer；
* 因测试失败而 defer；
* 因需要修改代码而 defer；
* 因存在未知而自动 defer；
* 用 defer 制造虚假的 Epic Completion。

原则：

> **Resolve when reasonably solvable. Defer when genuinely isolatable but not reasonably solvable now.**

---

# 11. Continue After Defer

一旦 Deferred Blocker 被合理隔离：

```text
Deferred Blocker
       ↓
Record
       ↓
Isolate affected scope
       ↓
Continue unrelated work
```

Agent MUST NOT 因一个 Deferred Blocker 停止无关 Capability。

---

# 12. Completion Status

CED 使用三个 Epic Execution Status。

---

## COMPLETED

定义：

> Epic 声明范围全部达到要求，并且不存在 Deferred Blocker。

---

## COMPLETED_WITH_DEFERRED_BLOCKERS

定义：

> 当前所有仍可合理推进和交付的部分均已推进完成，但存在已经明确隔离和记录的 Deferred Blocker。

核心语义：

```text
COMPLETED_WITH_DEFERRED_BLOCKERS
              ≠
           BLOCKED
```

它表示：

> **Agent 已经把当前可交付部分推进到底。**

它不得隐藏未交付 Capability。

Deferred 内容必须保持可见。Blocked capability MUST 保持 undelivered，不得进入 delivered capabilities、不得修改 ICD Acceptance Verdict、不得自动推进 Capability Pack State，也不得自动产生 `BUSINESS_READY`。

---

## BLOCKED

定义：

> 整个 Epic 已无法继续，并且触发合法 Stop Condition。

即：

```text
Unresolvable Execution Blocker
              OR
Required Human Decision
```

---

# 13. Status Decision

推荐决策：

```text
Epic work remaining?
      │
      ├─ NO
      │   ↓
      │ Deferred Blocker exists?
      │      ├─ NO  → COMPLETED
      │      └─ YES → COMPLETED_WITH_DEFERRED_BLOCKERS
      │
      └─ YES
          ↓
      Can continue?
          ├─ YES → CONTINUE
          └─ NO
              ↓
          Legal Stop Condition?
              ├─ YES → BLOCKED
              └─ NO  → find continuation path
```

---

# 14. Authority and Handoff

CED owns Epic continuation、defer、legal Stop Condition and completion semantics. It consumes evidence without taking over the producer's authority.

| Input / owner | CED use | CED MUST NOT do |
|---|---|---|
| ICD Acceptance | decide how the Epic proceeds around delivered or blocked capabilities | rewrite FAIL as PASS or count a blocked capability as delivered |
| FEV Verdict | assess whether further execution、isolation or defer is justified | override feasibility evidence |
| BMAD | explore alternatives when execution reveals design uncertainty | let research completion determine Epic status |
| OpenSpec / project engineering trace | locate authoritative scope、requirements、task state and completion report | invent a universal storage path or silently alter normative scope |

A blocked capability remains undelivered and cannot advance Project Delivery State or produce `BUSINESS_READY`. Reusable findings MAY flow to DOCS, but authoritative deferred blockers and completion reports stay with the Epic's OpenSpec / project engineering trace or an explicit link from it.

---

# 15. Proposal Completion Is Not Epic Completion

核心约束：

```text
Proposal Completed
       ≠
Epic Completed
```

Agent MUST 检查：

> Epic 中是否仍存在声明范围内尚未推进的工作？

如果存在：

`CONTINUE`

不得仅因为当前 Proposal 已 apply / implement / validate 而停止。

---

# 16. Failure Handling

遇到普通 failure：

```text
Failure
  ↓
Diagnose
  ↓
Can repair?
  ├─ YES → Repair → Validate → Continue
  └─ NO
      ↓
Alternative?
  ├─ YES → Try → Validate → Continue
  └─ NO
      ↓
Can isolate/defer?
  ├─ YES → Record → Continue
  └─ NO
      ↓
Legal Stop Condition?
```

Failure 本身不是 STOP Reason。

---

# 17. Retry Semantics

CED MUST NOT 使用机械规则：

`always retry N times`

合理尝试 SHOULD continue while：

* retry 能产生新的 evidence；
* conditions have changed；
* repair materially changes expected outcome；
* alternative path has not been tested；
* retry cost is reasonable relative to expected value。

当重复执行只是在复制相同失败且不产生新信息时：

> SHOULD stop repeating that path and move to another continuation strategy.

---

# 18. Dependency-Aware Continuation

Agent SHOULD 理解 Capability dependency。

例如：

```text
A → B → C

D
```

如果 B blocked：

* C 可能受影响；
* D 如果独立，则 SHOULD continue。

不得：

```text
B blocked
   ↓
Stop everything
```

除非 B 实际构成整个 Epic 的不可绕过 dependency。

---

# 19. Reordering

当原执行顺序受阻，但其他工作可以推进：

Agent MAY reorder。

例如：

```text
A → B → C → D
```

B 暂时 blocked，而 D 独立：

```text
A
↓
B blocked
↓
D
↓
return / defer B
```

Reorder 是合法 continuation strategy。

---

# 20. Workaround Boundary

Workaround MAY 用于继续 Epic，但不得伪造 Capability correctness。

如果 workaround：

* 改变 Capability semantics；
* 降低 Acceptance；
* 隐藏 failure；
* 绕过必要 correctness；

则不能偷偷视为正常完成。

应交给：

* ICD 判断 Capability Acceptance；
* FEV 判断必要的技术可行性；
* CED 判断是否继续 / defer / stop。

---

# 21. Final Epic Acceptance

CED 的连续执行结束不意味着 Agent 可以替代所有最终验收。

如果项目定义 Human Final Epic Acceptance：

```text
Agent execution complete
        ↓
Completion Status
        ↓
Evidence / Deferred Blockers
        ↓
Human Final Acceptance
```

Final Acceptance SHOULD 尽量集中在 Epic 边界，而不是每个内部 Proposal 边界。

---

# 22. Agent Default Behavior

Agent 执行 Epic 时 SHOULD：

```text
1. Understand Epic scope
        ↓
2. Identify capabilities / proposals / dependencies
        ↓
3. Execute next deliverable work
        ↓
4. Validate
        ↓
5. If PASS → continue
        ↓
6. If FAIL → diagnose
        ↓
7. Repair / retry / alternative
        ↓
8. Reorder / isolate / workaround when useful
        ↓
9. Defer only when justified
        ↓
10. Continue remaining deliverable work
        ↓
11. Stop only for legal Stop Condition
        ↓
12. Produce final Completion Status
```

---

# 23. Anti-Patterns

Agent MUST NOT：

* 一个 Proposal 完成就默认停止；
* 一个 Task 完成就默认停止；
* 普通测试失败就询问 Human；
* 普通代码错误就询问 Human；
* 发现替代实现就要求 Human 选择；
* 局部 Capability blocker 自动升级为 Epic blocker；
* 第一次失败立即 defer；
* 用 workaround 伪造 ICD PASS；
* 用 CED 覆盖 FEV Verdict；
* 用 CED 降低 Acceptance 标准；
* 因执行困难制造 Required Human Decision；
* 把 `COMPLETED_WITH_DEFERRED_BLOCKERS` 描述成完全无缺口的完成；
* 创建没有明确原因的 STOP；
* 为保持连续执行而隐藏失败。

---

# 24. Stop Report

如果最终 STOP，必须明确：

```yaml
stop:
  category: "Unresolvable Execution Blocker | Required Human Decision"
  blocker_or_decision: "<description>"
  affected_scope: "<scope>"
  evidence: "<evidence>"
  attempted_continuation:
    - "<repair / retry / alternative / isolate / defer attempts>"
  why_epic_cannot_continue: "<reason>"
  required_next_action: "<what is needed>"
```

不得只报告：

`Blocked. Need user help.`

---

# 25. Completion Report

CED owns Epic completion semantics，但不规定固定存储路径。authoritative report SHOULD 与 Epic 的 OpenSpec / project engineering trace 共址或由其明确链接；DOCS 不是 authoritative Epic state store。

Epic 结束时 SHOULD 报告：

```yaml
epic:
  status: "COMPLETED | COMPLETED_WITH_DEFERRED_BLOCKERS | BLOCKED"

delivered_capabilities:
  - "<capability>"

deferred_blockers:
  - blocker: "<blocker>"
    affected_scope: "<scope>"
    evidence: "<evidence>"
    current_icd_result: "<level / verdict / BLOCKED>"
    current_project_state: "<pack state>"
    suggested_next_action: "<next action>"

remaining_unattempted_scope:
  - "<scope, if any>"
```

如果状态为：

`COMPLETED`

则不得存在 Deferred Blocker 或声明范围内未处理的 required scope。

---
