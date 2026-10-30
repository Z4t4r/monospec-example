# pipelines

Trait：如何在仓库根目录 `pipelines/` 编写与维护**人类可读、可独立使用**的管线文档，以及 Cook / Evidence / Acceptance 合同。

**修订：** 2026-09-20 — 合并原入口硬规则中的 Evidence / Cook / Contract；Active 索引真源改为 domain `AGENTS.md`。  
历史版本由来源仓 archive 保存；portable package 不复制历史材料。

Agent 入口与选型 SOP 见 [`../pipelines/AGENTS.md`](../pipelines/AGENTS.md)。  
加载时机：新建 / 改写 / cook `pipelines/graphs/**` 之前 **MUST** 读本 trait 相关章节 + 入口全文。  
本 trait **只**留在 monospec `traits/`。**MUST NOT** 同步到 `repos/*/traits/`。

---

## `pipelines/` 是什么

- 短文档，记录资产或工具变更后**如何重跑已知实验 / 验收 Graph**。
- **不依赖** OpenSpec / 调研时间线即可 cook。
- **互斥 + 可组合**：同一 Goal 槽最多一条 `active` Graph；Subnet 经 Wire 串接。
- 产物可指认：Socket 声明态变；Context 锁定宿主对象。

## 它不是什么

| 层 | 路径 | 职责 |
|----|------|------|
| 调研 / 探索 | `docs/YYYY-MM-DD-*/` | 未定论试验、失败史 |
| 产品能力 | `openspec/specs/` | SHALL / Scenario |
| 变更工作 | `openspec/changes/` | proposal / design / tasks |
| **管线文档** | `pipelines/` | **已固化的验收 Graph + Gate** |
| **管线脚本** | 插件隔离目录 | Invoke / cook；默认未进业务 |

**不要**把仍在使用的「如何再验收 X」只写在调研夹编号文里。

## 与业务代码的隔离

1. 管线代码默认不进业务。  
2. 可为 Invoke 挂到插件，但 ≠ 产品化。  
3. 正式落地必须经 OpenSpec，且 change **明确参考**对应 Graph。  
4. 未落地脚本放隔离文件夹；文中标明 `experimental` / `isolated`。  
5. **禁止**隔离区 re-export 成业务公共 API。

落地路径：

```text
pipelines/graphs/<domain>/<slug>/ + 隔离脚本
        │  Gate
        ▼
openspec change（引用该 Graph）
        │
        ▼
插件业务 / 正式 UI
```

---

## 核心模型（DCC 同源）

| 概念 | 含义 |
|------|------|
| **Goal** | 某一终态的同一问题；槽位协议互斥 |
| **Graph** | 一条现行验收网络 |
| **Node** | 可 cook 或可 Gate 的单位 |
| **Subnet** | 复合 Node；默认可移植粒度 |
| **Socket** | 类型化交接口；态名 `<family>-<state>` |
| **Wire** | 上一段 Output = 下一段 Input |
| **Context** | 宿主内如何解析操作对象 |
| **Cook** | 执行变换或校验 |
| **Gate** | 显式声明的 dependency / decision；适用时不可静默通过 |
| **Invoke** | 如何触发 cook |
| **Contract** | 可机读的 input/output/invariants（推荐 `contract.yaml`） |
| **Runtime** | 执行环境（WHERE）；与 Graph WHAT 分离 |
| **Evidence** | Run 内证明产物 |
| **Acceptance** | 如何解释 Evidence（P0–P3） |

```text
Graph = WHAT
Contract = INPUT / OUTPUT
Dependency = WHAT FIRST
Runtime = WHERE
Cook = HOW
Evidence = PROOF
Acceptance = 解释（P3 = USER）
```

**Namespace：** Pipeline Evidence Acceptance 使用 `P0–P3`；ICD Capability Acceptance 使用 `L1–L4`。两者 MUST NOT 混写或相互推导。

---

## Kind / Family / Mutation

| kind | 含义 |
|------|------|
| `Graph` | 完整流程，可调用多个 Subnet |
| `Subnet` | 可组合单元；明确 start/end socket |

| family | 含义 |
|--------|------|
| `compose` | 端到端装配 |
| `transform` | 态变 |
| `probe` | 审计 / 诊断 / 预览；**不得**声称最终交付 |

| cook.mode | 要求 |
|-----------|------|
| `in-place` | 可改输入；必须明确 mutation scope |
| `new-object` | 保留输入；明确输出对象，防误认原件 |
| `mixed` | 逐对象说明；禁止隐式改输入「方便验收」 |

---

## Socket / Contract / Dependency

### Socket

```yaml
sockets:
  start: "<family-state>"
  end: "<family-state>"
```

`A.end == B.start` → 可 Wire。否则：adapter / Ask / 新 Contract。**禁止**自然语言猜兼容。

### Contract

会被其他 Graph 消费的 Graph **推荐**提供 `contract.yaml`：input/output state、object_type、coordinate_space、armature、invariants。  
**MUST NOT** 只在 prose 里描述关键接口，或让 Agent 从 `pipeline.md` 猜 input/output。

### Dependency

```yaml
dependencies:
  - id: <graph-id>
    type: graph
    required: true
```

禁止循环依赖、隐式依赖、通过 import 他 Graph 内部脚本实现依赖。依赖引用 **Graph ID**，不是脚本路径。

---

## Runtime

允许：

```yaml
runtime:
  adapter: blender
  version: "5.1"
```

```yaml
runtime:
  adapter: unreal-engine
  version: "5.8"
```

Blender Graph：**MUST** 遵守 [`python-dialect-trait.md`](./python-dialect-trait.md)；脚本 Python；**MUST NOT** Node/TS/pnpm。  
UE Graph：Editor / Python / Blueprint / API 属 Runtime 实现层；Graph 语义不得绑定临时 Editor 操作。  
版本不符 → `environment_mismatch`，不得假装正常 Cook。

---

## Cook 合同

Cook **MUST：**

1. 读 Graph / 校验 `status`  
2. 校验 dependencies / input Contract / Runtime  
3. 执行 transform / probe / compose  
4. 新建 run；写 Evidence（summary / report；仅显式用户验收时增加 acceptance）

Cook **MUST NOT：**

- 修改业务 Pipeline 定义或 acceptance 标准  
- 覆盖 / 删除旧 run 或失败证据  
- 自动宣布 Pipeline Evidence Acceptance P3 通过
- 为过 Gate 修改 `repos/` 业务实现  

Cook 前 **MUST** Invoke 查重：[`pipelines-cook-invoke` skill](../.cursor/skills/pipelines-cook-invoke/SKILL.md)。

`/gen-pipeline` ≈ propose（scaffold，不 Cook）。  
`/run-pipeline` ≈ apply（Cook + Evidence，不改业务/Contract/Acceptance）。

---

## Evidence 与 Acceptance（证明合同）

### Run（不可变）

- 每次 cook：`runs/<yyyy-MM-ddTHHmmss>/`  
- **禁止**覆盖旧 run；对比靠两份 run  
- `runs/` 默认不提交（见 `pipelines/.gitignore`）

### 标准文件

`summary.json`（机器主证）· `report.md` · 支持结论的 Evidence。`manifest.json` 按 provenance contract 保留。

`acceptance.md` 仅用于 Graph 显式要求的最终用户验收，不是每次 Run 的必需文件。FEV Run 不生成该文件、不等待人工 pass；Experiment discrimination criteria 保留在 experiment / contract 中，按 [FEV §33](./fev-trait.md#33-run-delivery-and-report) 交付 Verdict。

`report.md` MUST 先给本次运行的目的、执行范围、结果汇总与结论，再给关键 Evidence、失败原因、未执行项、限制与下一步影响。不得仅复制 JSON 或列 checks；失败 Run 也须给出报告。FEV 还须区分 Observation / Interpretation / Unknown，并说明 Verdict 的范围。

### Run Fingerprint（SHOULD）

记录 source / graph / config / runtime / environment 的 hash 或版本，避免不同输入混为同一历史证据。

### Result Status

| status | 含义 |
|--------|------|
| `pass` | 充分证据满足检查 |
| `fail` | 充分证据不满足 |
| `blocked` | 前置未满足，无法判断 |
| `invalid` | Run / Evidence 无效 |
| `skipped` | 明确未执行 |
| `source_missing` | 输入证据/资产不存在 |
| `environment_mismatch` | Runtime/版本/环境不符 Contract |

**`source_missing` ≠ `fail`**，除非 Acceptance 明文规定缺源即失败。  
**`No Evidence` ≠ `Pass`。**

### Evidence 优先于 Agent 判断

Agent **MUST** 依据 summary / report / Evidence / Contract；显式用户验收时再引用 acceptance。
**MUST NOT：** 凭截图猜数值；凭日志缺失猜成功；用 UI「看起来正常」宣布机器检查通过；用自然语言替代缺失 Evidence。

### 禁止自证闭环

禁止：验收失败 → Agent 改业务 → 再验 → Agent 宣布通过。  
Pipeline Agent 职责：执行 / 测量 / 记录 / 解释。

### 判定级别（Pipeline Evidence Acceptance P0–P3）

| 级 | 含义 | 谁判 |
|----|------|------|
| **P0** | 环境 / 基础运行 | Agent |
| **P1** | 机器可验证事实（存在性、计数、阈值、hash） | Agent |
| **P2** | 组合机器证据（alignment、mapping、export integrity） | Agent 可给 result，**必须引用 Evidence** |
| **P3** | Graph 显式要求的最终用户验收（观感、实机） | **仅用户**；仅适用时报告 `pending user review` |

- `overall_pass` **最多到 P2**。
- Agent **MUST NOT** 宣布 P3 PASS，或把根 acceptance 模板标为通过。
- 显式用户验收的 pass/fail **只改本次** `runs/<ts>/acceptance.md`；FEV 不适用 P3，不得默认等待用户批阅。

### 证据包（collector）

出报告的 Graph **宜**含 `## 证据包` 表：collector / required / sink（相对本次 run）。

1. 缺证必声明（`source: missing`）；禁止静默跳过。  
2. 先装收集器，再触发破坏性动作。  
3. 每次 run 至少 summary + report；acceptance 仅在显式用户验收时生成。

### probe 与 Evidence Scope

probe **MUST NOT** 伪装成 compose/transform 交付。  
每条 Evidence 必须能回答：哪个 Graph / Run / 输入 / Runtime / 检查 / Acceptance Level。

---

## 目录布局

```text
pipelines/
├── AGENTS.md
├── _template/
├── _shared/cook_runtime/
└── graphs/
    ├── <domain>/AGENTS.md          # Active 索引真源
    ├── <domain>/<slug>/
    │   ├── pipeline.md
    │   ├── config.yaml
    │   ├── contract.yaml           # 推荐
    │   ├── acceptance.md          # 仅显式用户验收；FEV 省略
    │   ├── scripts/
    │   └── runs/<ts>/
    └── _retired/<YYYY-MM>/<slug>/
```

- 路径与 slug：kebab-case。  
- **Active 索引写在 domain `AGENTS.md`**；根 `pipelines/AGENTS.md` 只指向 domain。  
- 证明落点是 `runs/<ts>/`，不是 `docs/YYYY-MM-DD-*/`。

---

## Node / Subnet / Graph 文档骨架

保持简短。成文多为 Subnet。

1. 标题 + 一句话目的  
2. Kind / Status / Goal  
3. Non-goals（含：不提交 runs；不宣布 P3）
4. Sockets + Cook mode  
5. Context（可机读键；禁止唯显示名）  
6. Requires / Assumes（耦合标 **coupled**）  
7. Cook chain（优先 mermaid）  
8. 证据包  
9. 判定级别  
10. Invoke / isolation  
11. Gate / Handoff  

Graph 文是装配投影，不是冻死巨石。默认可移植单位为 Subnet；耦合须诚实声明。

### 同 Socket 微调

已达 Output 后的补丁仍须 Validate/Gate；合同问题回写 Invoke，禁止只手改场景过 Gate。

### Compose

边必须 `previous.end == next.start`。不得跳过 adapter 硬连。

---

## 旧 → 新词汇

| 旧 | 新 |
|----|-----|
| e2e / 端到端装配 | Graph |
| stage | Node / Subnet |
| Input / Output artifact | Input / Output socket |
| Scene binding | Context |
| Transform | Cook |
| User confirmation | Gate |
| Entry points | Invoke |

---

## 独立性规则

1. 自称可独立则 Socket / Cook chain / Gate / Handoff 须写全。  
2. 诚实耦合。  
3. 跑实验不依赖 OpenSpec（落地进业务才依赖）。  
4. 知道下一步不依赖打开调研夹。  
5. 单向指针：`docs/` / `openspec/` 宜链到 `pipelines/`。  
6. 验收实验变了，先更新 Graph。  
7. 代码与业务隔离。  
8. 产物可指认。  

---

## 编写流程

1. 从调研提升已定论实验（去掉时间线与互斥考古）。  
2. 优先写成可移植 Subnet，再 Wire 进 Graph。  
3. 放入 `graphs/<domain>/<slug>/`；更新 **domain** `AGENTS.md` + `config.yaml`。  
4. 让调研指向管线。  
5. 脚本先隔离；产品化另走 OpenSpec。  

---

## 质量清单

1. 落在 `pipelines/graphs/`；入口 `AGENTS.md`（非 README）。  
2. 可 cook 的验收 Graph + Gate，不是未声明上线脚本。  
3. Status 清楚；Goal 互斥。  
4. Subnet 默认可移植；耦合声明。  
5. Sockets + Cook mode 明确。  
6. Context 可机读。  
7. Cook chain 有 mermaid（或 ASCII 降级说明）。  
8. Invoke 真实名称；未落地在隔离区。  
9. 已写入 **domain** Active 索引；`config.yaml` 完整 `graph.*`。  
10. 无未经 OpenSpec 并入业务的痕迹。  
11. 有证据包或显式「无机器证据、仅 Gate」。  
12. 说明适用的 P0–P2；仅业务 Graph 显式用户验收时配置 P3；FEV 按 Verdict 交付。
13. Non-goals 含不提交 runs / 不宣布 P3。
14. Result Status 区分 `source_missing` / `fail` / `environment_mismatch`。  
15. 未覆盖旧 run；缺证不静默跳过。  

---

## 反模式

- 现行协议只活在 `docs/YYYY-MM-DD-*/`。  
- 同一 Goal 两个 `active`。  
- 管线脚本直接进业务包 / 能跑就当正式功能。  
- 只有步骤、无 Socket；靠显示名认对象。  
- Cook 语义含糊；把 Gate 写成静默 Cook。  
- 无证据包却宣称已验；覆盖旧 run；缺证静默跳过。  
- Agent 宣布 P3 / 改根 acceptance 为 pass。
- 用 `overall_pass` 冒充实机或观感终局。  
- `source_missing` 当成 `fail`（无明文约定时）。  
- 自证闭环：改业务 → 再验 → 自宣通过。  
- probe 伪装成交付 Graph。  
- 依赖他 Graph 内部脚本路径而非 Graph ID。  
- 为 pipelines 引入 Node / TypeScript / pnpm。  

---

## 非目标

- 不替代 [`../pipelines/AGENTS.md`](../pipelines/AGENTS.md) 选型 SOP。  
- 不替代 OpenSpec 能力交付层级。  
- 不把本 trait 默认同化进子仓。
