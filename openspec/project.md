# MonoSpec Project Context

本仓是规范与编排 host；通过 [`.hagicode/monospecs.yaml`](../.hagicode/monospecs.yaml) 侧载多个 `repos/<project>/` 业务项目。具体产品目标与业务背景由目标项目补充，本包不带来源业务数据。

主仓负责 Trait、DOCS、Pipeline 和 OpenSpec；业务实现由各子仓的源码、runtime 与 tests 定义。子仓 metadata 见 [`../repos-meta/AGENTS.md`](../repos-meta/AGENTS.md)，根规则见 [`../AGENTS.md`](../AGENTS.md)。

Python Style 的唯一 authority 是 [`../traits/python-dialect-trait.md`](../traits/python-dialect-trait.md)。产品 SHALL 与 change 遵循 [`AGENTS.md`](AGENTS.md)，不以 bootstrap 或 Research 结果自动声明 delivered。