# repos-meta — 侧载项目契约

遵循根 [AGENTS.md](../AGENTS.md) 与 [MonoSpec 配置](../.hagicode/AGENTS.md)。

- 每个实际注册项目创建 `<project>/AGENTS.md`；其 `description` 字段指向该 metadata directory，源码对应 `repos/<project>/`。
- Metadata 记录职责、可写范围、上游边界、适用 Trait、build / validation 入口和跨树路由，不复制业务数据或源码。
- 遵循子仓真实约定；不能用 metadata 静默覆盖真实冲突或自动获得跨仓修改授权。
- 不保存 credential、local absolute path 或 private input。没有实际项目时不预建虚假 registry entry。