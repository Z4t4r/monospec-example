# Example Character — FEV Evidence 分析

```yaml
doc_type: EVIDENCE_ANALYSIS
lifecycle: ACTIVE
knowledge_state: CONFIRMED
date: 2026-10-30
root_fev: example-char
authority: DOCS analysis；Verdict 由 Graph Run 与 aggregate report 持有
```

## Run identity

| Run | Graph / Sub-FEV | 输入 | Local Verdict |
|---|---|---|---|
| `2026-10-30T153748` | example-character-export-fev / blender-export | spec，default_m | NOT_FEASIBLE（action 范围规则） |
| `2026-10-30T153814` | 同上 | spec，default_m | FEASIBLE |
| `2026-10-30T153931` | ue-import | `153814` | FEASIBLE（旧 contract，未检查 scale） |
| `2026-10-30T154126` | ue-import | `153814` | PARTIALLY_FEASIBLE |
| `2026-10-30T154153` | blender-export | spec，unit_cm | FEASIBLE |
| `2026-10-30T154154` | ue-import | `154153`（FBX sha256 `1daf93f3…`） | FEASIBLE |
| `2026-10-30T154907` | blender-export | spec，unit_cm（最终 script） | FEASIBLE（canonical） |
| `2026-10-30T154908` | ue-import | `154907`（FBX sha256 `5b332446…`） | FEASIBLE（canonical） |

环境：Blender 5.1.2；UE 5.8.4 CL58902052；host CPython 3.8。Run 位于各 Sub-FEV 的 `runs/`（gitignored）；每个 Run 的 `manifest.json` 记录 graph hashes、输入 sha256、lease 与 evidence hashes。

## Observation

1. Blender round trip（`154153`，`154907` 相同）：18 bones、136 vertices、2 materials、2 shape keys 全部保留；rest head 误差 2.6e-7 m，shape key delta 误差 1.6e-9 m。
2. Re-import 后 action 范围为 2–31，名称为 `Armature|Scene`（`153748`）。
3. `default_m` 输入在 UE 中：bones 与 component-space 位置都正确，但 `root` local scale = 100，子 bone local translation 以 m 为单位（`153931`、`154126`）。
4. `unit_cm` 输入在 UE 中：所有 bone local scale 为 1；ref pose 最大误差 6.7e-6 cm；MorphTarget `belly_out`、`head_scale_up`；material slots `M_Body`、`M_Head`；AnimSequence 30 keys / 29 frame intervals；18 条 bone track（`154154`，`154908` 相同）。
5. 同一 spec 两次导出的 inventory sha256 相同，FBX sha256 不同（FBX 文件内含导出时间），因此 Run 之间用 inventory 比较，不用 FBX hash。

## Interpretation

- H-axis 成立：Blender `(x, y, z)` m → UE `(x, -y, z)` cm；名为 `Armature` 的 node 不会成为额外 bone。
- 只比较位置会漏掉 root scale 问题：component-space 位置在两种 variant 下都正确，差别只出现在 local scale。这说明 check 设计需要覆盖“结构是否干净”，不能只看最终位置。
- `unit_cm` 让 export unit factor 为 1，因此 UE 不需要把 unit 转换写进 bone。

## Conclusion

Root FEV `example-char`：**FEASIBLE**，scope 为 `unit_cm` variant、上述 engine build 与 legacy FBX import path。详见 [aggregate report](../../pipelines/graphs/example/example-character-export-fev/aggregate/report.md)。

## Unknown 与 Limitations

- 未比较 MorphTarget delta、skin weight、动画曲线数值；未做 rendering。
- Interchange import path、其他 engine build、blended weight 角色为 `UNKNOWN`。
- 角色是 rigid box 角色，只代表结构与转换规则，不代表真实角色的视觉质量。
