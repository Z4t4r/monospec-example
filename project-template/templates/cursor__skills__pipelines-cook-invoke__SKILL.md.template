---
name: pipelines-cook-invoke
description: >-
  Verifies canonical Invoke for pipeline Node/Subnet Cook before running or
  implementing code in the target project; applies the post-cook fine-tune
  (补丁/微调) contract so scene patches re-Validate and absorb contract bugs
  into the active Invoke. Use when cooking pipelines, implementing or changing
  a Node Cook, fine-tuning after a pipeline already ran, writing the target project /
  isolation-dir pipeline scripts, calling Blender MCP execute_blender_code to
  transform assets, or when the user mentions Invoke, Socket cook, pipeline C,
  patch, 微调, or re-running an acceptance Graph.
---

# Pipelines Cook · Invoke 查重

在 **cook** 或 **新写/改写** 管线相关代码之前，先确认已有唯一现行实现。  
写作约定见 [`traits/pipelines-trait.md`](../../../traits/pipelines-trait.md)；选型入口见 [`pipelines/AGENTS.md`](../../../pipelines/AGENTS.md)；本 skill **不**复述 Graph/Node 文档结构。

## 硬规则

1. 同一 Socket 态变（`family-state-in` → `family-state-out`）在仓库里最多一个 **active** Invoke 落点。  
2. 有 canonical 符号 → **只调用**，禁止用 MCP `execute_blender_code`（或一次性脚本）内联重写同态变主 Cook。  
3. 缺实现 → 只在隔离区新建**一处**，并立刻写入对应 `pipelines/graphs/<domain>/<slug>/pipeline.md` 的 Invoke 表与 `config.yaml` adapters。  
4. 换算法 → 新符号 + 旧符号/`retired` + `pipelines/AGENTS.md` 继任；禁止两套并行 `active`。  
5. 管线已达 Output 后的微调遵守下方 **微调 Contract**（可直改本档，不可跳过 Validate / 不可只改场景不改合同代码）。

## 查重链（动手前按序执行）

| # | 动作 | 通过标准 |
|---|------|----------|
| 1 | 读 `pipelines/AGENTS.md` → `graphs/<domain>/<slug>/pipeline.md`（+ `config.yaml`） | 找到 `active`；同 Goal 无第二套 `active` |
| 2 | 读该文 **Invoke**（及 Code isolation / adapters） | 有可引用的 API / `bl_idname` / 脚本路径 |
| 3 | 在 the target project 或隔离区定位该符号 | `rg` / 读模块：符号存在且路径与文一致 |
| 4 | （可选）宿主探活 | 导入或 `bpy.ops…` 确认当前会话加载的是这一份 |
| 5 | 才允许 cook / 改代码 | 只经该 Invoke；Bind/探查可用临时代码，主 Cook 不行 |

任一步对不上 → **停**，说明是文档失真还是缺实现，问清后再动。禁止默默新开一版。

## 决策表

| 情况 | 行为 |
|------|------|
| Invoke 有、代码能定位 | 只调用该符号 |
| Invoke 有、代码找不到 | 停；修路径或补实现（先问人） |
| 无 Subnet、代码已有同 Socket 行为 | 先补/改 `pipelines/graphs/.../pipeline.md` + `config.yaml` 挂上 Invoke，再 cook |
| 真缺实现 | 隔离区单点新建 + 更新 Invoke；标 `experimental` / `isolated` |
| 想换算法 | retire 旧落点（`_retired/<YYYY-MM>/`）+ AGENTS 继任后再实现 |
| 已在 Output socket，只需微调 | 走 **微调 Contract**；勿默认整 Graph 重跑 |

## 微调 Contract（同 Socket 补丁 Cook）

适用：主 Cook / Graph **已经**把对象推到某 Output socket，之后发现细微问题；**不**要求重跑整条 Graph，**要求**出口合同再次成立。

### 分流（先定一类）

| 类 | 含义 | 必须做 |
|----|------|--------|
| **A. 合同 bug** | CookPython / 容差 / 漏步；下一份资产还会错 | 改 **唯一 active Invoke** 源码；对本档应用差值（局部 API / 补丁步 / 受控手改） |
| **B. 资产特例** | 仅本档 / coupled；不进通用合同 | 可直改本档；**不要**默写进主 Cook；可记 `docs/` 或 Subnet `coupled` |
| **C. 上游错态** | 实际不在声称的 Socket（塌缩 VG、错层、脏残留） | **禁止**叠微调；回滚 / 回源后走对应 Subnet |

### 固定步骤

```text
确认已处于声称的 Output socket（标记 + 指纹）
        → 分流 A | B | C
A/B     → 对本档应用差值（优先局部 Invoke；无则受控直改）
        → 同一套 Validate（overall_pass / 指纹）→ 核/写 pipeline_artifact
        → 写入本次 runs/<ts>/（summary + report；仅显式用户验收时 acceptance pending）→ Gate
A 另    → 确认 canonical 源码已含修复（否则下份资产回归）
```

### 约束

- **允许**直改当前产物；**不允许**只靠视口、跳过 Validate/Gate。  
- **不要求**重跑破坏性全链（如已 prune 再全量 dump）；优先局部步 + 全量校验（与 Switch「已达态 → 只 Validate」同向）。  
- 补丁若会反复用 → 升成 Cook chain 显式子步或局部 Invoke，写入 Subnet 文；禁止长期只活在 MCP 会话块里。  
- 微调**不**新开第二套 active 主 Cook；A 类是改现有落点。

### 反模式

- 手改场景过 Gate，CookPython 不改（A 类回归）。  
- 为吃上微调强制全量重跑破坏性 prune。  
- 把 B 类特例写进主 Cook，污染其它资产。  
- 在 C 类错态上继续叠补丁。

## MCP / 临时脚本边界

- **允许**：Bind、歧义消解、只读校验、调用已有 API/Operator、写报告路径旁路探查。  
- **允许（仅微调 Contract）**：对**已 Bind 且已在 Output** 的对象做差值修复；随后必须 Validate（+ Gate）；A 类必须回写 canonical Invoke。  
- **禁止**：把已有 Subnet 主 Cook 整段重写进 `execute_blender_code` 或 `docs/` 一次性脚本并当作现行入口。  
- 新脚本默认进插件隔离目录或仓库约定的 `scripts/` / `pipelines/` 隔离区，**不要**未开 OpenSpec 就并进业务公共 API。

## 与文档层的分工

- Trait / `pipelines/graphs/<domain>/<slug>/pipeline.md`：人读协议、Socket、Gate、Invoke **落点声明**；微调语义摘要见 trait「同 Socket 微调」。  
- `pipelines/AGENTS.md`：选型与索引；证据可用 `_shared/cook_runtime`（Python）。  
- 本 skill：Agent **动手前**查重，以及 **Cook 后微调** 的完整 Contract。  
- 产品化落地：仍走 OpenSpec，并引用对应 Graph（见 trait「与业务代码的隔离」）。
