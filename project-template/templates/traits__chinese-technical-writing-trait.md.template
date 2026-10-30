# chinese-technical-writing

Trait：中文技术文档的语言分工。简单骨架用常用中文；domain topic、专用名词、专用动词与复杂内容用英文，禁止硬翻译。尽量不用中文生僻词；需要时改用英文原文。

> 适用范围：本工作区内人工 / Agent 撰写或审阅的中文技术内容——`AGENTS.md` 正文、OpenSpec `proposal.md` / `design.md` / `tasks.md`、delta specs、`docs/` 专题文档、`pipelines/` 人读合同、commit message 的中文部分，以及 Agent 以中文作出的技术答复  
> 加载时机：新建或改写上述内容，或以中文描述软件 / 硬件 / 算法 / 程序行为 / 命令行之前 **MUST** 加载本 trait  
> 同步范围：本 trait 为文档写作契约，仅保留在 monospec 本仓 `traits/`；**MUST NOT** 同步到 `repos/*/traits/` 或子仓业务树  
> 迁移：约束**新写与触达改写**；不强制回写历史文档

## 角色定位

以**严谨的技术文档助理**执行本 trait：只陈述客观功能事实。中文只写简单、常用说明；叫什么、做什么、如何运作，用英文。

## 核心原则

> **简单内容用常用中文；domain topic、专用名词、专用动词、复杂内容用英文。禁止硬翻译。尽量不用中文生僻词；出现则改用英文原文。**

模板：

```text
常用中文骨架。English domain topic / identifier / verb / mechanism。常用中文收尾。
```

示例：

> 本 Graph 验收 `pose parity` 的 bone writeback：`solver` `evaluate_frame` 后写入 `FCompactPose`。L3 观感由用户 Gate。

## 语言分工

| 用常用中文 | 用英文（MUST；禁止硬译成纯中文技术段） |
|------------|----------------------------------------|
| 目的一句、范围、非目标 | **domain topic**：能力名、机制主题、调研 / change 主题、章节 topic、slug |
| 步骤顺序（先…再…） | **专用名词**：类型、API、标识符、资产类、Mode、格式名、协议名、产品名 |
| 谁验收、简单成败 | **专用动词**：`parse` / `evaluate` / `writeback` / `mute` / `bake` / `import` / `mount` / `overflow` / `catch` 等 |
| 连接与判断：因此、不得、属于 | **复杂内容**：transform chain、solver 语义、协议细节、`invariant`、parity / cross-check、失败 `mechanism` |

### domain topic

- **MUST** 使用英文原文或项目 slug（如 `pose parity`、`evaluate_frame`、`bone writeback`、`ue58-pose-parity`）。
- **MUST NOT** 把 domain topic 硬译成纯中文标题或术语后，再当全文唯一称呼。
- **允许**：`Bone writeback（骨变换写回）`——英文 topic 在前，中文释义至多一次；此后只用英文 topic。

### 专用名词与专用动词

- **MUST** 保留英文 lemma / 标识符；与源码、日志、API 对齐。
- **MUST NOT** 为「中文可读」发明界面译名替代 `Pose`、`bind pose`、`CompactPose`、`ConfigureProperties` 等。
- 简单句里的常用叙述词（是、有、位于、表示、完成）可用中文；一旦表示领域操作，改用英文专用动词。

### 复杂内容

若一句话需要自造中文术语才能说完，或译完无法与源码 / 日志对上：

- **MUST** 用英文写清机制；
- **MUST NOT** 写成无英文的长段纯中文技术说明。

### 中文用词（生僻词）

中文骨架 **MUST** 使用现代常用书面词，让非本领域读者也能读懂连接句。

- **MUST NOT** 使用生僻字、文言词、冷僻书面语，或只有小圈子才懂的中文技术译名。
- 若本想用中文，但只能想到生僻词 / 冷僻译名：**MUST** 改用英文原文（domain topic、专用名 / 动、或短英文短语），不要硬凑中文。
- **优先**：因此、所以、不得、先、再、完成、失败、范围、目的。  
- **避免后改英文**：如「收束」→ 写「收尾」或直接接英文结论；「不变式」→ `invariant`；「对拍」→ `parity` / cross-check；「机理」→ `mechanism`。

## 写作规则

| # | 规则 | 要求 |
|---|------|------|
| 1 | 简单骨架常用中文 | 目的、范围、顺序、验收角色用常用书面中文 |
| 2 | 技术内容英文 | domain topic、专用名 / 动、复杂机制用英文；禁止硬翻译 |
| 3 | 不用生僻词 | 中文只用常用词；生僻 / 冷僻译名改英文原文 |
| 4 | 禁用俚语与拟人 | 禁用隐喻义：吃、吞、啃、堆、爆、挂、干、薅、拉、刀；**MUST NOT** 把程序拟人化 |
| 5 | 不照搬社区口语 | **MUST NOT** 照搬圈子黑话；句子表意完整 |
| 6 | 命令行述事实 | 命令、参数、系统行为只述客观事实，不使用比喻 |
| 7 | 面板中文例外 | 引用插件中文面板文案时加引号，旁注对应英文能力名 |

## 禁用表达（隐喻）

左列仅可出现在反模式引用中：

| 禁用表达（反模式） | 推荐表述 |
|--------------------|----------|
| 内存吃紧、接口吃不消 | 内存不足；该接口无法承受该并发规模 |
| 把异常吞掉 | `catch` 该异常且不再向上抛出 |
| 啃源码 | 阅读源码 |
| 堆代码 | 编写代码；结构混乱 / 重复率高 |
| 爆内存 | integer / memory `overflow` |
| 服务挂了、进程挂掉 | 服务不可用；进程 `terminate` |
| 干掉进程 | `terminate` 该进程 |
| 薅数据 | `read` / extract 批量数据 |
| 从远端拉代码 | 执行 `git fetch` / `git pull` |
| Redis 帮你缓存 | Redis 将热点数据保存在内存中 |
| 本刀、下一刀、切刀 | `this change` / `next change`；按 capability boundary 划分 |

## 反模式对照

| 反模式 | 正确做法 |
|--------|----------|
| 在自动化导入时跳过属性配置并写回物理刚体数据（无英文） | automated import skips `ConfigureProperties`；`FactoryCreateBinary` writes `ConstraintData`（not `PhysicsAsset`） |
| 章节只写「骨骼写回」当唯一 topic | 正式 topic 用 `bone writeback`；可括号附一次常用中文释义 |
| 用「不变式 / 对拍 / 机理」等冷僻中文当术语 | 用 `invariant` / `parity` / `mechanism` |
| 这个服务一遇到高并发就挂 | 该服务在 high concurrency 下不可用 |
| 这行代码会吞掉所有异常 | 该代码块 `catch` 全部异常且不再抛出 |
| 把老代码干掉重写 | 删除旧实现并重新编写 |
| 优先用「解析 / 挂载 / 静音」作领域术语 | 用 `parse` / `mount` / `mute` |

## Agent 检查清单

- [ ] 简单骨架是否常用中文、表意完整？
- [ ] 中文是否避开生僻词 / 冷僻译名？该用英文的是否已改英文？
- [ ] domain topic 是否英文（或 slug），而非纯中文唯一称呼？
- [ ] 专用名词 / 专用动词是否英文，且未发明界面译名？
- [ ] 复杂机制是否有英文，而非硬译长段？
- [ ] 是否出现禁用隐喻（吃 / 吞 / 啃 / 堆 / 爆 / 挂 / 干 / 薅 / 拉 / 刀）？
- [ ] 是否把程序拟人化？
- [ ] 命令行与系统行为是否只含客观事实？

## 关联

- 索引：[`AGENTS.md`](./AGENTS.md)
- 根约定：[`../AGENTS.md`](../AGENTS.md)「文档语言」
- 调研对照：[`../docs/AGENTS.md`](../docs/AGENTS.md)「Output Language」
- 标准用语表：[`standard-words-trait.md`](./standard-words-trait.md)
