# Investigation Skill Draft

```yaml
doc_type: REFERENCE
lifecycle: ACTIVE
knowledge_state: PENDING_VALIDATION
date: 2026-10-30
candidate_skill: investigate-with-evidence
installation_state: NOT_INSTALLED
authority: 示例层 DOCS candidate；不是现行 Agent contract
```

## 状态

本文件把 [02 的执行说明](02-执行说明与验证.md) 展开为可评审的 skill 正文。它不在 `.cursor/skills/` 或其他 skill 目录中，因此不会被 discovery 或自动 trigger 加载。转为正式 skill 的条件见文末。

## Candidate discovery metadata

```yaml
name: investigate-with-evidence
description: 在本仓开展或接续跨阶段、存在重要技术不确定性的 investigation，组织目标、实验、知识更新及 FEV 到 ICD 的交接。适用于需要实际验证并持续推进的研究任务；单纯资料查询或普通已知修复不需要完整流程。
```

该候选依赖本仓的 FEV / ICD / DOCS / CED contract，不适用于没有这些契约的项目。

## Candidate SKILL.md body

### 目标与入口

把用户问题推进到有 Evidence 支持、能指导下一步的结论。先读根 `AGENTS.md`、适用的 subtree policy，以及 `traits/AGENTS.md` 路由到的 Trait。沿用现有 authority：FEV 判断 feasibility，ICD 判断 Capability Acceptance，CED 管理正式 Epic 的继续与停止，DOCS 保存可复用知识。

用户只要求资料分析、方案设计或局部实验时，按该范围完成；不要把 invocation 理解为自动启动整个 production workflow。简单、已验证的工作不强制建立 Root / Sub-FEV。

### 1. 恢复当前目标与实际状态

从用户请求、已有决定和 Topic Summary 确认：目标结果、非目标、已知 baseline、重要 Unknown、授权范围及用户要求的 checkpoint。

接续任务时，先把 handoff 与当前 Graph / change / Evidence 比较。已有结果变化时更新理解；旧环境中的 blocker 不自动适用于当前环境。只在关联内容会改变下一步判断时才展开 supporting documents。

缺少会改变路线的必要信息时提出具体问题；已有记录能回答的，不重复询问。

### 2. 建立与目标对应的路线

用最小、充分的设计表达从当前状态到目标的路径。每个重要阶段说明要回答的问题、输入、输出、依赖和结果用途。已有路线优先更新，不另建重复计划。

先区分已知事实、候选解释与待验证问题，再决定是否需要 FEV。按 independently testable uncertainty 拆分 Sub-FEV，不把任务清单机械转换为调查树。

提前确定结果的去处：design 保存 intended behavior；Graph / Run 保存 actual behavior 与 Evidence；DOCS 保存解释和可复用知识。文件数量由用途决定。

### 3. 执行最有价值的下一项实验

优先选择依赖已满足、能影响整体路线的问题。复用仍适用的 Evidence，再设计最小、有区分力的实验；写清实际环境、观察结果与判定条件，并按 domain contract 执行。

普通错误先定位和修复。失败揭示新 mechanism 或实现限制时，更新 hypothesis，尝试仍满足目标的替代路径；继续执行无法产生新的相关 Evidence 时，停止重复该路径，按现有 contract 判断后续。

发现上游问题时回到对应层修复，并识别受影响的 downstream input / Evidence。不把修改前的 Run 当作修改后的证明，也不机械重跑无关阶段。

### 4. 阶段结束时回到整体目标

有意义的结果或决定形成后，回答：

- 本次回答了什么，对整体目标和路线有什么影响？
- 哪些是已验证事实，哪些仍是解释或 Unknown？
- 哪些 design、canonical reference 或 reusable finding 需要更新？
- 当前授权内的下一项有价值工作是什么？

更新受影响的 authoritative artifact 和 DOCS 引用。汇报以目标进展、关键依据、限制与下一步为主；不逐轮转储聊天，也不要求每个阶段更新所有文件。

### 5. 继续推进与必要交互

局部实验完成后，在当前授权范围内继续依赖已满足的工作。不要因为写完报告、一个 Sub-FEV 完成或一次普通执行错误，就结束整个请求。

用户明确要求逐阶段选择时遵守；否则只在需要改变用户意图、缺少必要决定或有无法解决的执行 blocker 时提出具体问题。问题附已完成的可审阅结果、推荐及选择影响。已有批准继续有效。

研究问题已经充分回答时汇总结论，不为形式扩展实验；无法继续时记录实际 blocker、已尝试路径、影响范围与下一步需要什么。正式 Epic 的状态判断交给 CED，不在 DOCS 建立第二套执行状态。

### 6. 交接到实现或下一会话

问题被回答后，说明可行路径、适用条件、剩余 Unknown 和实施建议。研究任务可以在这里结束；只有取得适用的 Promotion 授权，才进入正式 change 与 production 实现。

进入实现时，把已验证的行为和接口作为输入，区分可复用内容与 experimental shortcut；按业务边界决定保留、重构或改写。对 production 实现独立执行 ICD；复用 FEV Evidence 前检查适用性，FEASIBLE 不自动成为 ICD PASS。

中断或换 Agent 时，按 [02 的 Handoff 内容](02-执行说明与验证.md#handoff-内容) 交接；接手方仍需核对当前事实。

## Draft 与现行契约的关系

| 内容 | 现行来源 | Draft 的作用 |
|---|---|---|
| Question、Experiment、Local / Aggregate Verdict | [FEV](../../traits/fev-trait.md) | 把局部问题与整体路线连接，不定义新 Verdict |
| L1–L4、Capability claim | [ICD](../../traits/icd-trait.md) | 在 production handoff 时应用，不重定义 PASS |
| 正式 Epic continuation / stop | [CED](../../traits/ced-trait.md) | 沿用已授权的工作边界，不建立 execution state |
| Topic、知识更新与 authority | [DOCS](../../traits/docs-trait.md)、[docs policy](../AGENTS.md) | 说明阶段结果何时回填，不复制完整 Run |
| Promotion 与业务 change | [OpenSpec policy](../../openspec/AGENTS.md) | 使用已有批准，不新增逐 stage 审批 |

## 试用场景

| 场景 | 应观察的行为 |
|---|---|
| handoff 已过时，但已有新的 canonical result | 先核对事实，复用有效工作，不按旧清单从头运行 |
| 一个局部实验成功，整体目标尚未回答 | 更新整体判断，在授权内继续下一项有价值工作 |
| 下游失败揭示上游假设错误 | 修正对应层，更新受影响的依赖与知识，不只在汇报中解释 |
| 用户只要求 research，或只批准一个 stage | 在该范围内产出可用结果，不自动进入 production |
| 用户已批准继续，遇到普通可修复错误 | 自行处理，不把普通修复变成重复审批 |
| 问题已经充分回答 | 给出结论与实施建议，不为完整流程制造实验 |

## 转为正式 skill 的条件

1. 在明确授权的真实任务中试用，按 [02 的验证维度](02-执行说明与验证.md#效果验证) 记录结果。
2. 确认它改善了工作衔接，且没有扩大任务范围或增加冗余步骤。
3. 用户明确要求后，才生成 `SKILL.md`、注册到 skill 目录并补充 routing；routing 只给短入口，保留现有 Trait authority。
4. 同步更新本 Topic 的 knowledge state 与 `topic.yaml` 的 `updated`。
