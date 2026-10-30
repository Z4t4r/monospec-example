# ICD — Incremental Capability Delivery

## Metadata

```yaml
trait:
  id: icd
  version: "1.0.0"
  date: "2026-09-22"
  status: "Established"
  type: "Engineering Method"
```

## Core Philosophy

**以能力交付为中心，而不是任务完成；先验收能力，再实现并完整交付。**

ICD 的基本工程单位是：

`Capability`

而不是：

`Task`

Agent 不应仅证明：

> “代码已经写完。”

而应证明：

> **“声明的 Capability 已经可以被目标用户或目标系统实际使用，并且达到对应 Acceptance Level。”**

核心原则：

> **验收 > 实现**

---

# 1. Capability Delivery

ICD MUST distinguish：

```text
Task Completed
      ≠
Capability Delivered
```

以下结果本身不能证明 Capability 已交付：

* 文件已经创建；
* TODO 已完成；
* function 已实现；
* class 已注册；
* build 成功；
* import 成功；
* 单个测试通过；
* Agent 声称实现完成；
* Proposal implementation 完成。

Capability Delivery 必须由对应 Acceptance Evidence 支持。

---

# 2. Capability as Delivery Unit

Capability SHOULD 描述：

> **目标用户或目标系统能够获得什么实际能力。**

良好的 Capability 通常具有：

* 明确目标；
* 明确使用场景；
* 可观察结果；
* 可验证 Acceptance；
* 明确范围；
* 明确 failure behavior。

避免仅使用实现任务定义 Capability。

例如：

```text
BAD:
Implement animation parser.

BETTER:
User can import a supported animation file and obtain
the expected animation result in the target system.
```

实现是手段。

Capability 是交付对象。

---

# 3. Acceptance Before Implementation

在进入完整实现之前，Agent SHOULD 尽早明确：

> **怎样的 Evidence 才能证明这个 Capability 已经交付？**

推荐顺序：

```text
Capability
    ↓
Acceptance Scenario
    ↓
Observable Evidence
    ↓
Implementation
    ↓
Acceptance Execution
    ↓
Verdict
```

而不是：

```text
Implementation
    ↓
“看起来完成了”
    ↓
临时寻找验收方式
```

因此：

> **Acceptance design SHOULD precede or accompany implementation design.**

---

# 4. Acceptance Levels

ICD 使用四级 Capability Acceptance Model。

---

## L1 — Basic Runtime Capability

定义：

**代码已经正确落位，能够进入目标运行环境，并且基础生命周期不崩溃。**

典型 Evidence：

* compile / parse 成功；
* import 成功；
* module load 成功；
* plugin register 成功；
* startup 不崩溃；
* 基础初始化成功。

L1 证明：

> **东西存在并且能够运行。**

L1 DOES NOT prove：

> **业务功能可用。**

因此：

```text
L1 ≠ Functional Delivery
```

---

## L2 — Core Business Capability

定义：

**目标用户最高频或最核心的 1–2 个场景能够端到端实际完成。**

必须存在可操作的用户/系统场景 Acceptance。

例如：

```text
User Action
    ↓
System Behavior
    ↓
Observable Result
```

仅以下内容通常不足以证明 L2：

* static analysis；
* import test；
* registration test；
* function existence；
* mocked internal call；
* implementation inspection。

L2 必须证明：

> **核心业务路径真的可以使用。**

---

## L3 — Complete Declared Capability

定义：

**Capability 声明范围内的 Requirements / Scenarios 已完整实现。**

包括：

* primary scenarios；
* secondary scenarios；
* declared edge cases；
* declared failure paths；
* invalid input behavior；
* user-visible/system-visible feedback；
* relevant configuration variants。

L3 的边界由：

**Declared Capability Scope**

决定。

L3 不要求支持未声明的无限场景。

---

## L4 — Regression-Protected Capability

定义：

**已经交付的 Capability 被正式 Regression Evidence 保护，并可持续验证。**

典型要求：

* regression tests 已进入 repository；
* tests 可重复执行；
* tests 当前 green；
* 关键历史 failure 被覆盖；
* 后续修改可以检测 capability regression。

L4 证明：

> **不仅现在工作，而且项目具备持续检测其退化的能力。**

---

# 5. Acceptance Level Is Explicit

Agent MUST NOT 模糊表达：

`done`

如果工程上下文要求 Acceptance Level，应明确：

```text
Capability: <name>
Target Level: L2
Result: PASS | FAIL | PARTIAL
Evidence: ...
```

Capability 达到 L1 时不得暗示已达到 L2。

Capability 达到 L2 时不得暗示已经满足完整 L3 scope。

---

# 6. Higher Level Includes Lower-Level Preconditions

通常：

```text
L4
↑
L3
↑
L2
↑
L1
```

更高 Acceptance Level SHOULD 建立在低层基本条件已经满足的基础上。

但 Agent SHOULD 避免为了形式而重复执行完全相同的验证。

已有可靠 Evidence 可以复用。

---

# 7. Interactive / Runtime Acceptance

当 Capability 本质上是：

* UI；
* editor interaction；
* runtime behavior；
* rendering；
* animation；
* workflow；
* import/export；
* user interaction；
* external-system integration；

ICD SHOULD 优先采用能够实际观察目标行为的 Acceptance。

例如：

* runtime execution；
* editor interaction；
* screenshots；
* readback；
* generated assets；
* output comparison；
* logs；
* target-system state；
* user-visible feedback。

静态代码存在不能替代本质上需要 runtime evidence 的 Capability Acceptance。

---

# 8. Evidence Quality

Acceptance Evidence MUST 与 Capability Claim 对齐。

例如：

Claim：

> Skeletal animation is rendered correctly.

仅证明：

> bone transform values changed

可能不足以证明 rendering capability。

同样：

Claim：

> File can be imported successfully.

仅证明：

> parser function returns without exception

可能不足以证明完整 import workflow。

核心原则：

> **Evidence must observe the layer claimed by the Capability.**

---

# 9. Acceptance Graph / Pipeline

复杂 Capability MAY 使用：

* Pipeline；
* Graph；
* test harness；
* runtime probe；
* scripted workflow；
* screenshot sequence；
* evidence bundle；

来组织 Acceptance。

但：

```text
Pipeline ≠ Capability

Graph ≠ Capability

Test ≠ Capability
```

它们是：

**Capability Acceptance Carrier**

而不是交付对象本身。

---

# 10. Failure Is Valid Evidence

Acceptance FAIL 是合法工程结果。

Agent MUST NOT：

* 为了宣布完成而降低 Acceptance 标准；
* 删除失败场景；
* 修改 threshold 以掩盖失败；
* 用静态检查替代失败的 runtime acceptance；
* 将 PARTIAL 描述为 PASS。

正确流程：

```text
Acceptance FAIL
       ↓
Diagnose
       ↓
Repair
       ↓
Re-run Acceptance
```

是否继续 Epic，由 CED 决定。

---

# 11. Capability Scope

每个 Capability SHOULD 有明确声明范围。

至少回答：

* Capability 是什么？
* 谁/什么系统使用？
* Primary Scenario 是什么？
* 哪些场景属于声明范围？
* 哪些场景明确不属于范围？
* Target Acceptance Level 是什么？

ICD MUST NOT 自动把：

`Capability`

扩大成：

`所有可能相关功能`

---

# 12. Incremental Delivery

ICD 中的 Incremental 指：

> **复杂系统可以按 Capability 增量交付，但每一个被宣布交付的 Capability 本身必须达到声明的 Acceptance。**

它不意味着：

> “每次写一点代码就算一次交付。”

推荐：

```text
Capability A
  ↓ Acceptance
Delivered

Capability B
  ↓ Acceptance
Delivered

Capability C
  ↓ Acceptance
Delivered
```

最终组合形成更大的 Product / Epic Delivery。

---

# 13. Capability Dependency

Capability MAY 依赖其他 Capability。

Agent SHOULD 明确：

```text
Capability B
depends on
Capability A
```

如果 A 尚未达到 B 所需的 Acceptance Level，则 B 不应被错误宣布为 Delivered。

但独立 Capability 不应因为无关 Capability FAIL 而自动 FAIL。

---

# 14. Acceptance Artifact

对于重要 Capability，Acceptance SHOULD 产生可追踪 Artifact。

可能包括：

* test result；
* logs；
* screenshots；
* generated output；
* comparison data；
* acceptance report；
* Pipeline run；
* Graph result；
* regression test；
* runtime measurement。

Artifact 的目标是：

> **让未来 Agent / Human 能够理解为什么这个 Capability 被判定为 PASS。**

不是为了制造文档数量。

---

# 15. Acceptance Evidence Reuse

如果已有 Evidence：

* environment 仍适用；
* Capability semantics 未改变；
* relevant implementation 未发生破坏性变化；
* evidence 仍足够回答当前 Acceptance；

Agent MAY reuse。

不要机械重复昂贵 Acceptance。

但如果关键条件已经变化：

> SHOULD revalidate.

---

# 16. Authority and Handoff

ICD owns declared Capability scope、target Acceptance Level、evidence interpretation and PASS / FAIL / PARTIAL result.

| Related system | Boundary |
|---|---|
| FEV | answers whether a proposed path is feasible; ICD still judges delivered behavior |
| CED | consumes ICD result to manage Epic continuity; MUST NOT rewrite FAIL as PASS |
| OpenSpec | supplies normative requirements and scenarios; ICD supplies acceptance evidence without changing SHALL |
| DOCS | MAY preserve design、evidence link and result reference; MUST NOT decide PASS |

ICD MUST NOT stop an Epic merely because one Capability fails; that decision belongs to CED. FEV Verdict、ICD Acceptance、Project Delivery State and CED Execution Status remain independent dimensions with no implicit promotion.

---

# 17. Agent Default Behavior

处理 Capability 时，Agent SHOULD：

```text
1. Identify Capability
        ↓
2. Identify declared scope
        ↓
3. Determine target Acceptance Level
        ↓
4. Define acceptance scenarios
        ↓
5. Define observable evidence
        ↓
6. Check dependencies / feasibility risk
        ↓
7. Implement
        ↓
8. Execute acceptance
        ↓
9. Evaluate evidence
        ↓
10. PASS / FAIL / PARTIAL
        ↓
11. Repair and revalidate when necessary
        ↓
12. Record durable acceptance evidence
```

只有 Evidence 支持声明时才能宣布 Capability Delivered。

---

# 18. Delivery Claim Rule

任何类似以下声明：

* Done
* Completed
* Implemented
* Delivered
* Finished
* Supported
* Working

如果语义上表示 Capability 已完成，MUST 能够追溯到对应 Acceptance Evidence。

如果只是代码完成，应明确描述为：

`Implementation completed`

而不是：

`Capability delivered`

---

# 19. Anti-Patterns

Agent MUST NOT：

* 把 Task Completion 当 Capability Delivery；
* 把 L1 当 L2；
* 用静态检查替代需要 runtime 的 L2/L3 Acceptance；
* 在实现完成后才临时降低 Acceptance 标准；
* 为获得 PASS 修改 Evidence threshold；
* 将 PARTIAL 描述为 PASS；
* 因单个 Capability FAIL 自动停止整个 Epic；
* 因 Epic 需要继续而伪造 Capability PASS；
* 把 Pipeline / Graph / Test 本身当作 Capability；
* 无限扩大 Capability Scope；
* 为了 L4 制造没有 regression value 的测试。

---
