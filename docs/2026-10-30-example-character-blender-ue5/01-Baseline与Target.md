# Example Character — Baseline 与 Target

```yaml
doc_type: REFERENCE
lifecycle: ACTIVE
knowledge_state: CONFIRMED # baseline 由 Run 与 repository 状态确认
date: 2026-10-30
authority: DOCS；Target 的验收口径由 Graph contract 与 OpenSpec 持有
```

## Baseline（开始前）

| 项 | 状态 |
|---|---|
| 资产 | 无。示例不得包含外部模型、贴图或动画，因此角色必须由脚本生成 |
| Blender | 本机 5.1.2，只允许 `--background` |
| UE | 本机 5.8.4，只允许在 AIAGENT Worker 中运行；Human Editor 不参与 |
| 共享工具 | `cook_runtime`、`fev_parallel` 已在模板中；没有 Blender / UE launcher |
| 业务代码 | `repos/` 为空；没有 exporter |

## Target

用户目标：模板里有一个包含 Blender 与 UE5 的完整案例，且不含来源项目的资产和敏感内容。

转为可验证的 target：

1. 角色：18 bones（single root `root`）、rigid skinned mesh、2 个 shape keys、2 个 material slots、1 个 30 帧 action。
2. Blender 侧：headless build 与 FBX export 可重复，re-import 后结构与数值不变。
3. UE 侧：自动 import 得到 native Skeleton / SkeletalMesh / MorphTarget / AnimSequence；bones、reference pose、bone scale、morph 名称、material slots 与动画长度一致。
4. Production：上述能力进入 `repos/example-character-tools` 的业务模块，并由独立 ICD Graph 验收。

## 非目标

Rendering、shading、physics、Control Rig、retarget、blended skin weight、texture。

## 已知 Unknown（开始时）

- FBX 的 axis 与 unit 转换在 UE 中的实际结果（H-axis）。
- Blender re-import 是否保留 action 的帧范围与名称。
