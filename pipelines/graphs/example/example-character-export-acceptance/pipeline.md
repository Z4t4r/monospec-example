# example-character-export-acceptance

Kind: **Graph** · Status: **active** · Family: **compose** · Cook: **new-object** · ICD target: **L3**。

Goal：验收 OpenSpec change [`add-example-character-export`](../../../../openspec/changes/add-example-character-export/proposal.md) 的 production 实现 `repos/example-character-tools`。参考数据是 FEV canonical inventory（[Root FEV aggregate](../example-character-export-fev/aggregate/report.md)）；本 Graph 只读取该数据，不 import FEV script。

## 非目标

- 不修改 `repos/` 代码以使 check 通过；失败时回到 OpenSpec change 修复实现。
- 不声明 L4：Blender / UE runtime check 没有进入 CI。
- 不做 rendering 与 retarget（FEV `UNKNOWN`）。

## Checks

完整规则见 [`contract.yaml`](contract.yaml)。

| Level | Check | 场景 |
|---|---|---|
| L1 | `L1-unit-tests`、`L1-addon-register`、`L1-cli-exit` | 代码可在 host 与 Blender 内加载；add-on register / unregister；CLI 运行 |
| L2 | `L2-ue-assets`、`L2-ue-skeleton`、`L2-ue-ref-pose`、`L2-ue-morph-material-anim` | 核心场景：CLI 导出 → UE5.8 Worker import 得到干净的 native asset |
| L3 | `L3-fev-parity`、`L3-operator`、`L3-invalid-input` | Operator 入口、与 FEV canonical 一致、invalid input 失败路径 |

P0（engine version、Worker lease、Worker exit）失败时整个 Run 为 fail。

## Invoke

在 repository root 执行（需要 `.local/environment.yaml`）：

```powershell
python pipelines/graphs/example/example-character-export-acceptance/scripts/run_acceptance.py
```

脚本输出 `RUN=<path>`；Run 位于 `runs/<yyyy-MM-ddTHHmmss>/`（gitignored）。

## 证据包

| collector | sink |
|---|---|
| summary（checks + `icd.levels` / `achieved_level`） | `summary.json` |
| report | `report.md` |
| provenance（production 文件 sha256、FEV canonical sha256、environment、lease） | `manifest.json` |
| raw evidence（unit test log、Blender log、CLI 输出、Worker readback） | `evidence/` |

## Acceptance record

| Run | 结果 | Achieved |
|---|---|---|
| `2026-10-30T154958` | 13/13 pass | L3（参考数据读自 `runs/`，已改为 tracked canonical） |
| `2026-10-30T155119` | 13/13 pass | **L3**（L1 / L2 / L3 PASS；L4 未声明）；当前记录 |

Capability claim 以 Run 的 `summary.json` 为准；本表只做索引。
