# BMAD — Requirements Engineering & Decision Research

## Metadata

```yaml
trait:
  id: bmad
  version: "1.0.0"
  date: "2026-09-22"
  status: "Established"
  type: "Requirements / Research Capability"
```

## Core Philosophy

**通过启发、探索与研究，把模糊 Intent 转化为更清晰的需求认知和候选方向。**

BMAD 负责：

> **帮助想清楚。**

BMAD 不负责：

> **证明做得到。**

也不负责：

> **把 Capability 最终交付出来。**

最重要的边界：

```text
BMAD = Inspirational / Exploratory

BMAD ≠ Engineering Proof
BMAD ≠ Capability Acceptance
BMAD ≠ Continuous Delivery
```

---

# 1. Purpose

BMAD 是 Agent 可调用的：

**Requirements Engineering / Decision Research Toolbox**

它用于处理：

* 模糊 Intent；
* 不完整需求；
* 多种可能方向；
* 用户尚未明确的约束；
* 技术路线探索；
* 候选方案发现；
* trade-off 分析；
* PRD / SPEC 前期形成。

BMAD 的价值是：

```text
Ambiguous Intent
      ↓
Elicitation
      ↓
Exploration
      ↓
Research
      ↓
Candidate Directions
      ↓
Clearer Requirements
```

---

# 2. Capability-Based, Not Command-Based

Blueprint MUST model BMAD by：

**Capability**

而不是：

**具体 command 名称。**

Agent MAY 使用 BMAD 提供的：

* brainstorming；
* ideation；
* elicitation；
* interactive Q&A；
* research；
* web search；
* candidate discovery；
* comparative analysis；
* trade-off analysis；
* PRD drafting；
* SPEC drafting；
* other relevant exploratory capabilities。

但 Trait MUST NOT 假定某个固定 BMAD command 永久存在。

原因：

> Tool / Command / Workflow 可以变化，但 Engineering Semantics 应保持稳定。

---

# 3. No Mandatory Full Workflow

Agent MUST NOT 对每个 Intent 强制执行完整 BMAD Workflow。

应根据 Intent maturity 选择必要能力。

例如：

```text
Very vague Intent
      ↓
Brainstorm
      ↓
Elicitation
      ↓
Research
      ↓
Candidate directions
```

而对于已经明确的需求：

```text
Clear Intent
      ↓
Focused Research
      ↓
SPEC refinement
```

甚至：

```text
Already clear + low uncertainty
      ↓
BMAD may be unnecessary
```

BMAD 是工具箱，不是固定 ceremony。

---

# 4. Intent Elicitation

当用户 Intent 模糊时，BMAD MAY 通过：

* Q&A；
* assumptions；
* examples；
* counterexamples；
* scenario exploration；
* constraint discovery；
* edge-case questioning；
* priority clarification；

帮助形成更明确的需求。

目标不是无限提问。

目标是：

> **消除会实质影响方案或 Scope 的需求不确定性。**

---

# 5. Brainstorming

BMAD MAY 主动提出：

* alternative interpretations；
* candidate features；
* implementation directions；
* product possibilities；
* architecture ideas；
* risks；
* missing requirements；
* edge cases。

但 Brainstorming 输出默认是：

```text
IDEA / CANDIDATE / HYPOTHESIS
```

不是：

```text
VERIFIED FACT
```

---

# 6. Research

BMAD MAY 使用：

* web research；
* official documentation；
* technical articles；
* community knowledge；
* existing project docs；
* source inspection；
* comparative research；
* domain references。

Research 可以回答：

* 有哪些已知方案？
* 行业通常怎么做？
* 官方支持哪些 API？
* 哪些方案值得进一步验证？
* 有哪些明显 trade-off？
* 哪些风险需要 FEV？

Research 的目标是：

> **扩大并改善决策空间。**

---

# 7. Candidate Solution Discovery

BMAD MAY 输出一个或多个 Candidate Solution。

每个 Candidate SHOULD 尽可能包含：

* basic idea；
* expected advantages；
* known disadvantages；
* assumptions；
* known constraints；
* unknowns；
* risks；
* evidence source；
* feasibility questions requiring validation。

Candidate Solution 默认状态：

```text
PROPOSED
```

或：

```text
RESEARCHED
```

不得自动标记：

```text
FEASIBLE
```

---

# 8. Comparative Analysis

BMAD MAY 比较候选方案，例如：

| Dimension        | Candidate A | Candidate B |
| ---------------- | ----------- | ----------- |
| Complexity       | ...         | ...         |
| Known support    | ...         | ...         |
| Integration cost | ...         | ...         |
| Risks            | ...         | ...         |
| Unknowns         | ...         | ...         |

比较结果用于：

> **帮助理解 trade-off。**

它不自动构成：

> **目标环境中的 Engineering Verdict。**

---

# 9. PRD

BMAD MAY 根据 Intent 和 Research 形成 PRD。

PRD 可以描述：

* problem；
* user；
* goals；
* non-goals；
* scenarios；
* requirements；
* constraints；
* success criteria；
* product decisions。

但 PRD 不是每次 BMAD 调用的强制产物。

如果需求不需要 PRD：

> MUST NOT 为了流程完整机械生成 PRD。

---

# 10. SPEC

BMAD MAY 帮助形成或完善 SPEC。

SPEC 可以描述：

* requirements；
* behaviors；
* scenarios；
* interfaces；
* constraints；
* expected outcomes。

但：

```text
SPEC written
    ≠
Engineering feasibility proven
```

SPEC 描述：

> **我们希望系统满足什么。**

FEV 验证：

> **候选方案在目标环境是否真的能够做到。**

---

# 11. PRD and SPEC Are Independent Tools

Blueprint MUST NOT 强制：

```text
PRD → SPEC
```

作为所有 Intent 的固定路径。

允许：

```text
Intent → PRD
```

也允许：

```text
Intent → SPEC
```

也允许：

```text
Intent → Research → SPEC
```

也允许：

```text
Intent → Brainstorm only
```

Agent 应根据任务需要选择。

---

# 12. Inspiration Boundary

这是 BMAD 最重要的工程边界。

> **BMAD 仅负责启发性工作。**

这里的“启发性”包括：

* requirement discovery；
* clarification；
* brainstorming；
* research；
* candidate generation；
* comparative analysis；
* PRD；
* SPEC drafting。

即使 BMAD 输出非常完整，也仍属于：

```text
Understanding / Exploration / Proposal
```

而不是：

```text
Verified Engineering Reality
```

---

# 13. Claim Classification

BMAD SHOULD 区分：

### USER INTENT

用户明确表达的目标或要求。

### RESEARCHED FACT

来自可靠外部来源的事实。

### PROJECT FACT

来自当前项目 evidence 的已知事实。

### INFERENCE

根据现有信息推导出的判断。

### HYPOTHESIS

需要进一步验证的解释。

### CANDIDATE

值得考虑的方案。

### UNKNOWN

当前信息不足。

不得将这些类别静默混合。

---

# 14. Research Does Not Prove Feasibility

以下证据：

* 官方文档说支持；
* Stack Overflow 有实现；
* GitHub 有类似项目；
* 博客说可以；
* 搜索结果显示有人做过；
* framework API 存在；
* source code 看起来支持；

可以提高 Candidate Solution 的可信度。

但如果关键问题是：

> **在当前目标环境、版本、execution path 和约束下是否真的可行？**

则：

```text
Research
   ↓
Candidate / Hypothesis
   ↓
FEV
   ↓
Evidence
   ↓
Feasibility Verdict
```

---

# 15. Authority and Handoff

BMAD owns Requirements Engineering、decision research 与 Candidate discovery；它不签发 engineering proof、Capability Acceptance 或 Epic completion status。

| Handoff target | BMAD supplies | Target authority |
|---|---|---|
| FEV | candidate、claim、source、assumption、feasibility question | FEV independently issues Verdict from target-environment evidence |
| ICD | intent、requirement、scenario、declared scope | ICD defines and judges Capability Acceptance |
| CED | alternatives and decision context discovered during execution | CED decides continue、defer or legal stop |
| OpenSpec | requirement candidate、rationale、comparison | OpenSpec owns adopted normative SHALL / change |
| DOCS | reusable research、decision context、source links | DOCS preserves knowledge state and authority without upgrading claims |

BMAD output remains inspirational/exploratory after handoff. Entering OpenSpec or DOCS does not turn a researched candidate into feasibility proof, delivered capability or completed Epic.

---

# 16. Agent Invocation Rule

Agent SHOULD 根据 Intent maturity 判断是否调用 BMAD。

典型触发：

### Ambiguous Intent

使用 elicitation / brainstorming。

### Multiple plausible directions

使用 candidate discovery / comparison。

### Missing domain knowledge

使用 research。

### Need formal requirement artifact

使用 PRD / SPEC drafting。

### Important feasibility uncertainty

BMAD MAY identify candidates，但 SHOULD hand off to FEV。

### Already clear and sufficiently grounded

BMAD MAY be skipped。

---

# 17. Minimal Sufficient Exploration

BMAD SHOULD 避免无限探索。

继续 Research / Brainstorming 应至少满足一个条件：

* 能显著改善需求理解；
* 能发现新的合理 Candidate；
* 能解决重要 trade-off；
* 能识别新的关键风险；
* 能减少重要 UNKNOWN；
* 能帮助形成必要 PRD / SPEC。

如果继续探索已经很难改变决策空间：

> SHOULD stop exploration and hand off to the next engineering stage.

---

# 18. Agent Default Behavior

当 BMAD 被触发时：

```text
1. Understand current Intent maturity
        ↓
2. Identify important unknowns
        ↓
3. Select only necessary BMAD capabilities
        ↓
4. Elicit / brainstorm / research
        ↓
5. Separate facts / inference / candidates / unknowns
        ↓
6. Compare plausible directions when useful
        ↓
7. Produce clearer requirements or candidate directions
        ↓
8. Identify feasibility questions
        ↓
9. Hand feasibility uncertainty to FEV when necessary
        ↓
10. Hand formal requirements to the appropriate engineering system
```

---

# 19. Anti-Patterns

Agent MUST NOT：

* 强制每个任务执行完整 BMAD Workflow；
* 把 BMAD command 名称固化成长期 Blueprint semantics；
* 把互联网 Research 当作工程 feasibility proof；
* 把 Candidate Solution 写成 verified solution；
* 把 Hypothesis 写成 Fact；
* 强制所有 Intent 同时生成 PRD 和 SPEC；
* 为流程完整制造无价值文档；
* 无限 Brainstorm；
* 无限 Research；
* 用 BMAD 替代 FEV；
* 用 BMAD 替代 ICD；
* 用 BMAD 替代 CED；
* 因 BMAD 研究结束宣布 Capability Delivered；
* 因 BMAD 研究结束宣布 Epic Completed。

---
