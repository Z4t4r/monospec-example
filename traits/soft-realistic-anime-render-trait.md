# soft-realistic-anime-render

Trait：按 **Soft Realistic Anime**（半写实二次元）做 Blender 角色渲染指导。目标是柔软、有透光、有体积，而不是塑料，也不是 `MToon`。

本文件是该画面目标下的回答契约。  
**不是**人设宣言，**不是**验收 Graph，**不是**参数圣经。下面的数值是**起步范围**；看到模型尺寸、引擎或截图后 **MUST** 改，禁止把起步值当成唯一正确答案。

加载时机：用户要角色渲染、皮肤 Shader、布光、景深、Compositor，或明确要 Soft Realistic Anime / 半写实皮肤（含成人向画面的材质与灯光技术）时，**MUST** 先读全文。  
本 trait **只**留在 monospec `traits/`。**MUST NOT** 同步到 `repos/*/traits/`。

专用名词用英文（`Principled BSDF`、`Subsurface`、`Eevee`、`Cycles`、`Rim Light`）。叙述用中文。见 [`../docs/AGENTS.md`](../docs/AGENTS.md)。

## 它是什么

指导如何在 Blender 里把 已导入角色渲染成 Soft Realistic Anime：

- 皮肤有透光，高光柔，不蜡、不灰、不炸色
- 光有主次和体积，不靠一盏灯 Uniform 照平
- 布料、丝袜、金属、珠宝有质感，不一概 `Roughness = 0.5`
- 引擎差异写清楚；成人向材质与湿润、布料、灯光可以直说技术，不说教

## 它不是什么

| 不是 | 去哪 |
|------|------|
| 游戏导出 / 材质烘焙 | 对应 `pipelines/graphs/`；烘到 `Principled BSDF` 贴图 ≠ 本 trait 的渲染外观 |
| 目标插件的角色 domain | [`../repos-meta/AGENTS.md`](../repos-meta/AGENTS.md) |
| 写 `.py` | 先 [`python-dialect-trait.md`](./python-dialect-trait.md)。本 trait 默认给节点与参数，不默认写脚本 |
| Cook 协议 | [`pipelines-trait.md`](./pipelines-trait.md) |
| 未成年或年龄不明的性化渲染 | **停止**。本 trait 只覆盖明确的成人角色 |

## 回答顺序

### 先诊断，再开方

用户给了截图、渲染图或文字描述时：

1. **先**指出当前失败（塑料、蜡、`Subsurface` 溢色、噪点、平光、无 `Rim Light`、景深糊错、过度 Glare）。
2. 引擎未知则 **先问** `Eevee` 还是 `Cycles`。两套参数 **MUST NOT** 混用。
3. 只改导致该失败的环节。不要把五段流程整份倒出去。

### 复现一种画面时，按此顺序

用户要「做成某种风格 / 这种气氛」且不是单点报错时，**MUST** 按顺序给建议，可简可详，不可跳步把后期当主手段：

1. 灯光布局
2. 皮肤 Shader
3. 材质细节
4. 摄像机与 `Depth of Field`
5. `Compositor`

后一步 **MUST NOT** 用来掩盖前一步没做完（例如用 Glare 冒充 `Rim Light`，用调色盖住蜡状 SSS）。

## 引擎

| | `Cycles` | `Eevee` |
|--|----------|---------|
| 皮肤透光 | 主路径。`Random Walk (Skin)`（Material 若有 Subsurface method） | 近似。Weight 低于 Cycles，否则泛光、溢色 |
| 承诺 | 可以追求本 trait 的透光皮肤 | **MUST NOT** 承诺与 Cycles `Random Walk` 等观 |
| 噪点 | SSS 样本不足会脏；先降 Scale / Weight，再加采样，不要先靠 Denoise 糊掉细节 | 用阴影柔化与光的尺寸；不要把 Cycles 的 Light Path 建议抄过来 |
| 体积光 | Volume 可以弱用 | 体积更假；宁可少用，把气氛交给光比和雾状 World |

未声明引擎时，皮肤与湿润配方默认按 `Cycles` 写，并标明「`Eevee` 需另给一套」。

## 灯光

相对强度比节点数值更稳。给建议时 **MUST** 写清：光型、相对大小、色温或冷暖、相对强度。不要只给一个与曝光无关的 Watt。

起步（肖像，角色已占画面主体）：

| 灯 | 作用 | 起步 |
|----|------|------|
| Key | 主塑形，软 | 大 `Area Light`；暖，约 4500–5500 K；相对强度 `1` |
| Fill | 抬阴影，不抢主光 | 更弱、更散；相对 `0.15–0.35`；不要第二盏同样亮的 Key |
| Rim | 轮廓与暧昧边缘 | 侧后；相对 `0.4–0.8`；可偏冷 6500–8000 K，或一点紫 / 品红点缀，不要和 Key 同色同强 |
| World / HDRI | 环境与微弱填光 | 强度压低，使 Key 仍是造型来源。HDRI 只负责环境色，不负责主光 |

- 柔软来自灯的**尺寸**和距离，不来自把所有灯调白。
- 要暧昧体积：Key 偏侧、阴影留得住、Rim 只描边。正面平光是反模式。
- 冷暖对比放在 Key vs Rim（或 vs 弱 World），不要满场景同一色温。

## 皮肤 Shader

节点：**一个** `Principled BSDF` 做皮肤主体。连接逻辑先于长脚本：

- `Base Color` ← 角色 albedo（可略降饱和，避免 SSS 后更红）
- `Subsurface Weight` / `Radius` / `Scale` 只加在皮肤材质，**不要**套到牙、眼、金属
- 湿润 / 出汗用 `Coat`（Weight + 较低 `Coat Roughness`），不要把 `Roughness` 拉到 0 冒充湿
- 高光用 `Roughness` + `Specular IOR Level`，不要再叠一层与皮肤无关的强 Emission

### 给 Scale 之前 MUST 先看尺寸

`Subsurface Scale` 跟对象真实尺寸走。角色导入后，角色高度可能是约 1.6 m，也可能是 0.1 量级。

- 尺寸未知 → **先要**视口里角色高度（或 `Dimensions`），再给 Scale。
- **MUST NOT** 在未知尺寸时抛一个固定 Scale。

角色约 **1.6 m** 高、`Cycles`、`Random Walk (Skin)` 时的起步（不是合同）：

| 参数 | 干皮肤 | 出汗 / 湿润 |
|------|--------|-------------|
| `Subsurface Weight` | `0.15–0.35` | 同上或略低；湿主要靠 `Coat`，不要靠把 Weight 拉满 |
| `Subsurface Radius` | 偏红，约 `(1.0, 0.25, 0.12)`–`(1.0, 0.40, 0.20)` | 同左 |
| `Subsurface Scale` | `0.006–0.018` | 同左 |
| `Roughness` | `0.35–0.55` | `0.18–0.32` |
| `Specular IOR Level` | `0.35–0.55` | `0.45–0.7` |
| `Coat Weight` | `0–0.08` | `0.12–0.35` |
| `Coat Roughness` | — | `0.05–0.18` |

身高不是 1.6 m 时，Scale 按高度比例改：`scale ≈ 表内值 × (身高米 / 1.6)`。导入缩放极端时，以测到的高度为准，不用文件名猜。

溢色：Radius 的 G/B 过高，或 Weight 过高。先收 G/B 与 Weight，不要先在 Compositor 里去饱和「救」皮肤。  
噪点：Scale 过大或 Weight 过高时，采样再高也脏。先收参数，再加样本。

`Eevee`：Weight 用上表下限或更低；接受透光更假。不要把 Cycles 的 Radius 原样当 `Eevee` 成品。

## 材质细节

目标是「软、有物性」。默认反塑料：`Roughness` 不要全材质 0.5，金属不要 `Metallic = 1` 且 `Roughness = 0`。

| 表面 | 起步方向 |
|------|----------|
| 布 | `Roughness` `0.45–0.75`；软布可加低 `Sheen Weight`（约 `0.15–0.4`）。法线适中，不要把布作法线贴图噪音墙 |
| 丝袜 | 薄、低到中 `Roughness`，弱透或薄 `Coat`；**不要**用玻璃 `IOR 1.45` 当丝袜 |
| 金属 / 珠宝 | `Metallic` 高，`Roughness` 按磨损留 `0.15–0.45`；珠宝高光靠光的形状，不靠 Emission |
| 法线 / 粗糙度贴图 | 有则接入对应插槽，强度保守。没有贴图时用数值，不要假装有贴图节点 |

二次元夸张体型上的布料穿插、物理、权重：只在用户问形变 / 穿模 / 布料时进入。材质问题不要改去修骨骼。导入后若皮肤仍是 toon / `MToon` 一类，要本风格则 **MUST** 换成 `Principled BSDF`，不要在 toon rim 上叠 SSS 冒充半写实。

## 摄像机与景深

- 肖像焦段大约 `50–85 mm`（以传感器等效理解）。广角拉近会毁「柔」，除非用户要那种形变。
- `Depth of Field`：焦点在近眼（或用户指定的焦点）。光圈起步 `f/1.8–f/2.8`。焦外是空气，不是整脸糊。
- 构图和灯光没定时 **不要**先开景深。

## Compositor

只在前四步能看出主体之后做。

- 允许：轻对比、轻冷暖分离、很弱的 Glare。
- 禁止：用强 Bloom 伪造 Rim；用压黑隐藏坏 SSS；用整图去饱和掩盖溢色。
- `Eevee` 的 Bloom 通常已经偏强；`Cycles` 不要把 `Eevee` 的 Glare 强度抄过来。

## 成人向技术

画面含湿润皮肤、贴身布料、暧昧布光、R18 构图时：

- **直接写** Shader、灯光、摄像机参数。不回避，不说教，不把技术问题改写成道德评论。
- 只给渲染所需的节点与数值。**MUST NOT** 另写与参数无关的色情叙述。
- 主体是未成年，或年龄不明却按未成年表现 → **停止**，不给参数、不给节点。

## 反模式

| 反模式 | 正确做法 |
|--------|----------|
| 一个 `Principled BSDF`、`Roughness 0.5`、无 SSS，称为二次元皮肤 | 按引擎给 Weight / Radius / Scale，或说明为何这张图不该开 SSS |
| 未知身高就给死的 `Subsurface Scale` | 先要 `Dimensions` |
| `Eevee` 与 `Cycles` 同一组 SSS | 分列 |
| 用 `MToon` / toon rim 当 Soft Realistic 皮肤 | 皮肤改为 `Principled BSDF` |
| 复现风格时先调 Compositor | 灯光 → 皮肤 → 材质 → 相机 → 后期 |
| 用 Glare 假装 `Rim Light` | 加侧后光 |
| 湿皮肤把 `Roughness` 打到 0 | `Coat` + 中低 `Roughness` |
| 丝袜用玻璃 BSDF | 薄布 / 弱透 + 低到中粗糙 |
| 因为内容成人就拒答材质与灯光 | 成人角色可以直说技术 |
| 为未成年提供性化渲染参数 | 停止 |
| 把本 trait 写成 Graph 或业务脚本 | 咨询用本文件；脚本另走 python-dialect |

## Agent 检查清单

- [ ] 是否先判断失败点，而不是直接贴一整棵节点树？
- [ ] 引擎是否标明？`Eevee` / `Cycles` 是否分开？
- [ ] 复现风格时是否按灯光 → 皮肤 → 材质 → 相机 → Compositor？
- [ ] `Subsurface Scale` 是否在已知身高之后才给数字？
- [ ] 数值是否是范围，并写了相对光比，而不是孤立 Watt？
- [ ] 是否用后期掩盖灯光或 SSS 问题？
- [ ] 成人向是否只停留在技术参数？未成年是否已停止？
