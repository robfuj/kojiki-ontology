# Kojiki Decision System / Kojiki 意思決定システム / Kojiki 决策系统

**将任何LLM转变为以决策为中心的组织的本地优先、开源框架。**

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![Tests Passing](https://img.shields.io/badge/Tests-All%20Passing-brightgreen.svg)](#testing)
[![OpenViking Compatible](https://img.shields.io/badge/OpenViking-Compatible-orange.svg)](https://github.com/volcengine/OpenViking)

---

## 🌐 Language / 言語 / 语言

[**English**](README.md) • [**日本語**](README.ja.md) • [**中文**](README.zh.md)

---

## 🎯 这是什么？

Kojiki 为任何 LLM（Claude、GPT、本地模型、Agent 框架）提供**共享、可审计的决策结构**——而不仅仅是聊天。每个部门 Agent 都通过相同的 **SYNAPSIS 变换链** 进行推理：

```
RECORD → SACCADE → EVIDENCE → INTERPRETATION → STRATEGY → OUTPUT → OUTCOME → LEARNING
```

每个阶段都是**有边界的变换**，具有明确的权限和明确的"绝不可静默变成什么"（evidence ≠ interpretation ≠ belief ≠ doctrine）。**Brain** 编排；独立的 **Adversarial Audit（对抗性审计）** 质疑。跨部门协调通过 **MYCELIUM 冠层** 进行——一种去中心化的、需求驱动的基质，模仿菌根网络。

> **「当下是廉价的部分。」** 当你试图追溯决策为何被做出——什么证据支持它、什么假设失效了、治理门槛要求什么——结构就会证明其价值。

---

## 🏗️ 架构概览

### 双层设计（论文：`MYCELIAL-GOVERNANCE-COMPLETE-THESIS.md`）

| 层级 | 目的 | 关键属性 |
|------|------|----------|
| **Root（刚性层）** | 单个 Bot 的内部流水线 | 强制顺序、上下文隔离、`EVALUATION ≠ ORIGINATION` |
| **Canopy（涌现层）** | Bot 间协调 | 冗余路由、相互强化、无中央控制器 |

```
┌─────────────────────────────────────────────────────────────┐
│  MYCELIUM Canopy Tier（涌现协调）                            │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │Marketing│──│  Sales  │──│Finance  │──│Product  │ ...    │
│  │  Head   │  │  Head   │  │  Head   │  │  Head   │ 20     │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘ lines  │
│       │            │            │            │              │
│       ▼            ▼            ▼            ▼              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Signal Bus (propagate.py)  │  Reinforcement (Tero)   │   │
│  │  Pruning (reciprocity)      │  Centrality (computed)  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  SYNAPSIS Root Tier（每 Bot 刚性流水线）                      │
│  RECORD → SACCADE → EVIDENCE → INTERPRETATION → STRATEGY    │
│       → OUTPUT → OUTCOME → LEARNING                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │Runner.py│  │Schema   │  │Adversary│  │Brain    │        │
│  │context  │  │validate │  │Audit    │  │adjudicate│        │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### 三个垂直轴

| 轴向 | 组件 | 目的 |
|------|------|------|
| **水平** | MYCELIUM | 跨部门协调（OKR 基质） |
| **垂直** | NEURAXIS | 递归问题重定义（L0–L4 升级） |
| **先验** | SACCADE | 证据收集前的问题框架 |

### 来源层（SENTINEL）

每个信号、边变更和门控证据都包裹在**非同质化、哈希链式、Ed25519 签名的来源令牌**中——因此治理门槛的"N 个不同经验"标准计算的是*已验证的佐证*，而非捏造的声称。

---

## 🏛️ 7 层

| 层 | 回答的问题 | 范围 |
|------|-----------|------|
| **KOJIKI** | 什么存在 — 本体 | 实体、关系、20 个标准部门 |
| **SACCADE** | 尝试前问题是否恰当 | 先验、有界迭代框架（收敛或达上限） |
| **SYNAPSIS** | 单个有界决策如何产生 | 单 Bot、刚性、可审计 — Evidence ≠ Interpretation ≠ Strategy |
| **NEURAXIS** | 失败需沿抽象阶梯上溯多远才能解释 | 事后、仅实发散时升级、L3/L4 治理 |
| **MYCELIUM** | 多部门多决策如何保持协调 | 涌现 OKR 依赖图、子图级 Signal、非指令 |
| **SENTINEL** | 到底是谁说的 | 每个跨节点声明都有签名、哈希链、非同质化来源 |

---

## 🚀 快速开始

```bash
# 克隆决策系统
git clone https://github.com/robfuj/Narro  # 或你的 fork
cd decision-systems

# 安装完整包：本体 + 20 部门 + 2 个元 Agent
bash install-all.sh

# 或安装单个部门（如缺失会自动克隆本体）
cd 03-marketing
bash bots/install_bots.py brand growth
```

### 安装后

每个 Agent 首次运行时执行 **Kojiki Orientation Protocol（定向协议）**：
1. **Name + function** — 我是谁？
2. **Industry / sector** — 触发研究
3. **Jurisdiction**（国家 / 地区 / 监管）
4. **Geography + business model**
5. **Sibling registration** — 在 `handoffs/registry.json` 中父 `group_id` 下注册

随后 Agent 通过 SYNAPSIS 链运行工作，并用以下命令验证：
```bash
python3 ../00-kojiki-ontology/synapsis/validate.py --mycelium-registry ../00-kojiki-ontology/handoffs/registry.json bot-output.json
```

---

## 📁 仓库结构

```
decision-systems/
├── 00-kojiki-ontology/          # 共享大脑（核心）
│   ├── synapsis/                # SYNAPSIS 链 + 验证器
│   │   ├── SYNAPSIS.md          # 完整规范
│   │   ├── validate.py          # 不变量检查器（仅标准库）
│   │   ├── REFERENCES.md        # 咨询框架映射表
│   │   └── transformations.json # 阶段定义
│   ├── schemas/                 # 核心 JSON Schema（在 Bot 中镜像）
│   │   ├── evidence.json
│   │   ├── interpretation.json
│   │   ├── strategy.json
│   │   ├── problem.json
│   │   ├── learning-ledger.json
│   │   └── decision-object.json
│   ├── mycelium/                # Canopy 层（涌现协调）
│   │   ├── schemas/             # node, objective, key_result, edge, signal, provenance_token
│   │   ├── engine/              # registry, graph, reinforcement, propagate, prune, sentinel, saccade
│   │   ├── neuraxis/            # 垂直轴: experience, problem, gate_request, escalation
│   │   ├── tests/               # 全部通过
│   │   └── examples/            # demo_marketing_sales.py
│   ├── learning/                # 组织记忆（案例、模式、规则）
│   ├── handoffs/                # 跨部门注册表 + 交接标准
│   ├── decision-rights/         # Own/Recommend/Consult/Approve/Execute/Escalate/Automate
│   ├── consultant/              # yoichiojima-2/consultant（复制，MIT，设计时参考）
│   └── build_repos.py           # 生成 20 个部门仓库
│
├── 01-executive-strategy/       # 部门仓库（各自独立）
├── 02-finance/
├── 03-marketing/
├── 04-sales/
├── ... (共 20 个)
│
├── 21-executive-org-builder/    # 元：询问安装哪些高管 Agent
└── 22-decision-system-installer/# 元：安装整个栈
```

每个部门仓库包含：
```
03-marketing/
├── bots/
│   ├── install_bots.py          # 按需子功能安装器
│   ├── manifest.json            # 子功能 + transformation_pipeline
│   └── <slug>/                  # 每个子功能一个（如 brand, growth）
│       ├── AGENT.md             # 入口点 + 定向协议
│       ├── runner.py            # 上下文隔离流水线执行器
│       ├── pipeline/            # 5 阶段提示词
│       │   ├── 01-saccade.md
│       │   ├── 02-evidence.md
│       │   ├── 03-interpretation.md
│       │   ├── 04-strategy.md
│       │   └── 05-output.md
│       ├── schema/              # 00-kojiki-ontology Schema 镜像
│       ├── data/                # example.json（存根决策对象）
│       └── tools/validate.py    # 扩展验证器
└── README.md
```

---

## ⚙️ 核心概念

### SYNAPSIS 变换链（刚性层）

| 阶段 | 权限 | 绝不可变成 | 输入 | 输出 Schema |
|------|------|------------|------|-------------|
| **RECORD** | 发生了什么 | — | 原始输入 | `decision-object.json` |
| **SACCADE** | 真正的问题是什么？ | EVIDENCE, STRATEGY | `raw_record` | `problem.json` (P-0000) |
| **EVIDENCE** | 来源确立了什么？ | INTERPRETATION, STRATEGY | `raw_source`, `prior_accepted_evidence` | `evidence.json` (Verified Extracts) |
| **INTERPRETATION** | 证据意味着什么？ | EVIDENCE, STRATEGY | `accepted_evidence` | `interpretation.json` |
| **STRATEGY** | 应该做什么、何时做？ | EVIDENCE, INTERPRETATION | `accepted_interpretation` | `strategy.json` |
| **OUTPUT** | 如何执行？ | EVIDENCE, INTERPRETATION, STRATEGY | `accepted_strategy` | `output.json` |
| **OUTCOME** | 实际发生了什么？ | — | 现实 | `decision-object.json` (更新) |
| **LEARNING** | 提取模式 | — | 结果 vs 期望 | `learning-ledger.json` |

**`runner.py` 强制的不变量**（承重组件）：
- `inputs_forbidden` **不提供**给模型调用——比"请不要"更强
- 每阶段 = 作用域内的独立模型调用
- `validate.py` 对照 Schema + 不变量规则检查输出

### MYCELIUM Canopy 层（涌现）

| 基元 | Schema | 关键规则 |
|------|--------|----------|
| **Node** | `node.schema.json` | `id = parent + "." + local`（血统强制） |
| **Objective** | `objective.schema.json` | 灵活时间范围（非强制季度） |
| **Key Result** | `key_result.schema.json` | `status` + `confidence` + `depends_on[]` |
| **Edge** | `edge.schema.json` | 跨职能交接字段；权重由互惠性强化 |
| **Signal** | `signal.schema.json` | 必需 `diagnosed_cause` + 14 类别分类法；子图边界 |

**运行周期**（每边、每评审）：
```
KR 状态变更 → Signal（原因 + 类别） → Subgraph（阈值 0.15）
→ Propagate（非指令） → Reinforce/Decay/Prune → 下一周期
```

**强化**（Tero et al. 2010，离散版）：
```
weight = weight * (1 - decay) + rate * (flow_signal ** gamma)
# gamma=1.15 默认；越低 = 越冗余/耐故障
```

**剪枝**（寄生防护）：
```
prune if weight < 0.05 OR reciprocity < 0.2
# reciprocity = reciprocal_exchanges / (reciprocal + one_directional)
```

### NEURAXIS（垂直轴）

| 层级 | 范围 | 自主性 |
|------|------|--------|
| **L0** Execution | 修正输入重试 | 自主 |
| **L1** Reasoning | 修正推理 | 自主 |
| **L2** Problem Representation | 替换 Problem 对象 | 自主 |
| **L3** Ontology | 修正本体关系 | **需要治理门控** |
| **L4** Meta-Strategy | 修正选择机制 | **需要治理门控** |

治理门控（§VII.5.5.1）：重复阈值（N 个不同经验）、决策权利、带故障关闭默认值的 SLA。

### SENTINEL（来源证明）

| 属性 | 实现 |
|------|------|
| **签名** | Ed25519，私钥仅由节点运行时持有 |
| **非同质化** | `entry_id = hash(payload_hash + signer + prev_entry_id)` |
| **链** | 每日志（`signals.jsonl`, `edges_history.jsonl`, `gate_evidence.jsonl`） |
| **验证** | 提交前 + 治理门控计算证据前 |

---

## 🧪 测试

```bash
cd 00-kojiki-ontology/mycelium
PYTHONPATH=../ python3 tests/test_registry.py
PYTHONPATH=../ python3 tests/test_graph.py
PYTHONPATH=../ python3 tests/test_reinforcement.py
PYTHONPATH=../ python3 tests/test_propagate.py
PYTHONPATH=../ python3 tests/test_prune.py
PYTHONPATH=../ python3 tests/test_sentinel.py
# 所有测试通过
```

运行演示示例：
```bash
PYTHONPATH=../ python3 examples/demo_marketing_sales.py
```

---

## 📚 研究与参考文献

架构建立在四个独立领域的同行评审研究之上：

### 生物学（菌根网络）
| 研究 | 发现 | 架构映射 |
|------|------|----------|
| Tero et al., *Science* (2010) | Physarum 强化/衰减在无中央规划者下收敛于高效、耐故障的拓扑 | MYCELIUM 强化公式（§IV.6.1）、γ 效率-冗余权衡 |
| Gorzelak et al., *AoB Plants* (2015) | CMN 介导的植物通讯主流案例 | 信号传播基础（§II.2, §IV.6.3） |
| Song et al., *PLoS ONE* (2010); Babikova et al. (2013) | 防御信号传播（"priming"） | 仅限作用域的子图 Signal 传播 |
| Karst, Jones & Hoeksema, *Nature Ecology & Evolution* (2023) | 怀疑性综述：CMN 文献中正效应研究的引用偏倚 | §II.5 的警示——仅构建在有充分支持的机制上 |
| Frew et al., *Functional Ecology* 专刊 (2025) | CMN 是异质的，依赖语境/宿主/真菌类型 | 强化 §II.5 的警示 |
| Silvestri et al. (2025), *New Phytologist* 状态报告 (2026) | AM 共生中发现新分子调控机制（`ckRNAi`） | §II.6——细胞层被证明越来越刚性 |
| Bilgen & Akan, "Internet of Plants" (2024–2025, Cambridge/Koç) | 独立通信工程形式化：真菌网络作为"基于图的通信媒介" | 验证 `SIGNALING ≠ ORCHESTRATION` 不变量（§IV.3, §II.7） |
| Adamatzky, *Royal Society Open Science* (2022) | 真菌电脉冲显示类似基本代码的统计结构 | 标记为投机性（§II.4），非承重 |

### 神经科学（层级预测编码）
| 研究 | 发现 | 架构映射 |
|------|------|----------|
| Rao & Ballard (1999) | 层级预测编码：预测向下，残差误差向上；误差上升直到被吸收 | NEURAXIS 升级梯（§VII.5.2）——完全相同的计算结构 |
| 脊髓 → 延髓 → 大脑皮质反射弧 | 快速局部反应；模糊刺激升级；皮质抑制调节反射 | NEURAXIS L0–L4 层，L3 处设治理门控 |

### 免疫学（先天/适应性免疫边界）
| 研究 | 发现 | 架构映射 |
|------|------|----------|
| 先天免疫（TLR，固定）→ 适应性免疫（抗体，记忆） | 适应性用学习层补充先天；从不重写先天识别机制 | NEURAXIS 治理门控：L0–L2 自主，L3–L4 需外部验证（§VII.5.2, §VII.5.5） |

### LLM 强化学习研究
| 研究 | 发现 | 架构映射 |
|------|------|----------|
| 稀疏轨迹级奖励 → 过程级信用分配 | 逐步信用分配用更少数据产生更好学习 | SYNAPSIS 分阶段分解，`diagnosed_cause_category` 来自 Learning Taxonomy |

### 企业级多 Agent 参考架构
| 来源 | 发现 | 架构映射 |
|------|------|----------|
| Microsoft 多 Agent 参考架构（真实部署） | 注册表 → 编排器 → 知识/状态 → 异步重放感知通信 | 独立到达相同组件分离 |

### 递归自我改善分类法
| 研究 | 发现 | 架构映射 |
|------|------|----------|
| 有界（L3）vs 无界（L4/L5）自我改善 | 有界：改进机制外部维护 | `LEARNING ≠ PERMISSION TO REWRITE DOCTRINE` 不变量将系统保持在 L3 |

---

## 🔧 咨询框架（设计时参考）

SYNAPSIS 阶段映射到标准咨询框架——不是运行时依赖，而是填补特定缺口的**命名方法**：

| 框架 | 映射机制 | 章节 |
|------|----------|------|
| **5 Whys / Fishbone** | Adversarial Audit 根因 | §III.1 |
| **MECE / Issue Tree** | EVIDENCE 分解、INTERPRETATION 非重叠 | §III.1, III.2 |
| **Pyramid Principle / SCQ** | PRODUCTION 答题优先输出 | §III.1 (OUTPUT) |
| **案例框架** | 领域特定 STRATEGY 模板 | §III.1 (STRATEGY) |
| **RACI** | 决策权利模型 | §VII.5.5.1, §III.2 |
| **Balanced Scorecard** | Hermes KPI 架构 | §III.2 |
| **PDCA** | MYCELIUM 运行周期 | §IV.7 |
| **Sensitivity Analysis** | γ / decay_rate / 阈值校准 | *开放项* |

完整映射：`synapsis/REFERENCES.md`  
框架复制自：`consultant/` (yoichiojima-2/consultant, MIT, 无 `.git`)

---

## 🛣️ 路线图

| 阶段 | 焦点 | 状态 |
|------|------|------|
| **v1** | 刚性层（SYNAPSIS）+ 涌现层（MYCELIUM）+ NEURAXIS + SENTINEL | ✅ 完成 |
| **v2** | Task 3 确定性评分、CI py_compile、通过/失败阈值、Schema 版本控制、扩展演示矩阵 | 📋 计划中 |
| **v3** | 阶段输出对抗性重新推导、全 20 部门改造、制品交叉验证 | 📋 计划中 |

详见 `MYCELIAL-GOVERNANCE-COMPLETE-THESIS.md`。

---

## 🤝 贡献

1. **无闭源依赖** — 所有代码 MIT，外部引用仅 AGPL-3.0 (OpenViking)
2. **本地优先** — 在 qwen2.5:14b (M1 Max 32GB) 运行，无需云端
3. **提供商无关** — 将任何 LLM 指向 `AGENT.md`
4. **必须测试** — PR 前运行 `python3 -m py_compile` + 验证器通过
5. **仅设计时参考** — `consultant/` 是副本，非依赖

---

## 📄 许可证

MIT — 见 [LICENSE](LICENSE)。

OpenViking（可选记忆后端）为 AGPL-3.0，外部，不打包。

---

## 🔗 链接

- **论文**: `MYCELIAL-GOVERNANCE-COMPLETE-THESIS.md`（双层架构、生物学、治理）
- **参考映射**: `synapsis/REFERENCES.md`
- **咨询框架**: `consultant/`（50+ 框架、斜杠命令）
- **演示**: `mycelium/examples/demo_marketing_sales.py`

---

**Kojiki Decision System. 不留未审计的决策。**