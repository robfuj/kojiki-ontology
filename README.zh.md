# Kojiki Decision System / Kojiki 意思決定システム / Kojiki 决策系统

**将任何LLM转变为以决策为中心的组织的本地优先、开源框架。**

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![Tests Passing](https://img.shields.io/badge/Tests-All%20Passing-brightgreen.svg)](#testing)

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
│  │Marketing│──│  Sales  │──│Finance  │──│Engineer │ 7      │
│  │  Head   │  │  Head   │  │  Head   │  │  Head   │ lines  │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
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

## 🏛️ 7 个合并部门

| 部门 | 范围 |
|------|------|
| **Finance** | Budget, CAC, ROI, FP&A, treasury |
| **Marketing** | Brand, growth, referral, paid media |
| **Sales** | Outbound, growth, Biz Dev, Corp Dev |
| **Engineering** | Product, Customer Success, Technology, Referral tech |
| **Operations** | Supply chain, procurement, day-to-day ops |
| **Legal** | Compliance, Risk, contracts, regulatory |
| **People & Comms** | HR, Internal comms, Public Affairs |
| **Technology Platform** | AI, IT, Security, Data Analytics |

---

## 🚀 快速开始

```bash
# 克隆决策系统
git clone <your-repo-url>
cd decision-systems

# 安装完整包：本体 + 7 部门 + 元 Agent
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
5. **Sibling registration** — `handoffs/registry.json` 中父 `group_id` 下注册

随后 Agent 通过 SYNAPSIS 链运行工作，并用以下命令验证：

```bash
python3 ../synapsis/validate.py --mycelium-registry ../handoffs/registry.json bot-output.json
```

---

## 📁 仓库结构

```
decision-systems/
├── synapsis/                    # SYNAPSIS 链 + 验证器
│   ├── SYNAPSIS.md             # 完整规范
│   ├── validate.py             # 不变量检查器（仅标准库）
│   ├── REFERENCES.md           # 咨询框架映射表
│   └── transformations.json    # 阶段定义
├── schemas/                    # 核心 JSON Schema
│   ├── evidence.json
│   ├── interpretation.json
│   ├── strategy.json
│   ├── problem.json
│   ├── learning-ledger.json
│   └── decision-object.json
├── mycelium/                   # Canopy 层（涌现协调）
│   ├── schemas/                # node, objective, key_result, edge, signal, provenance_token
│   ├── engine/                 # Core MYCELIUM engine modules
│   ├── neuraxis/               # 垂直轴: experience, problem, gate_request, escalation
│   ├── tests/                  # 全部通过
│   └── examples/               # demo_marketing_sales.py
├── sentinel/                   # 来源层: Ed25519, 哈希链
├── learning/                   # 组织记忆（案例、模式、规则）
├── handoffs/                   # 跨部门注册表 + 交接标准
├── decision-rights/            # Own/Recommend/Consult/Approve/Execute/Escalate/Automate
├── consultant/                 # 50+ 咨询框架（复制，MIT，设计时参考）
├── var/                        # 运行时数据（gitignore: 日志、哨兵密钥）
├── README.md / .ja.md / .zh.md
├── PROMO.md
└── LICENSE

├── kojiki/                      # 统一运行时
│   ├── core/                   # 共享执行引擎
│   │   ├── runner.py           # Slim orchestrator（约500行）
│   │   ├── stages/             # 8 阶段执行子
│   │   └── __init__.py         # Specialist loader, call_model, schemas
│   ├── specialists/            # 7 specialist configurations
│   │   ├── ai-intelligence/
│   │   ├── engineering-platform/
│   │   ├── finance-accounting/
│   │   ├── legal-compliance/
│   │   ├── marketing-brand/
│   │   ├── operations-ops/
│   │   ├── people-hr/
│   │   └── sales-outbound/
│   ├── configs/                # 部门负责人 + 参谋长配置
│   │   ├── dept-heads/
│   │   └── chief-of-staff.yaml
│   └── cli.py                  # 简单 CLI: `kojiki decide "goal"`

├── scripts/                    # 验证和 CI
│   ├── verify_all_runners.py
│   ├── verify_causal_signatures.py
│   └── test_runner_group.py

├── shared/                     # 共享资源（符号链接）
│   ├── prompts/                # 8 阶段提示词
│   └── schemas/                # 11 JSON Schema

├── test_governance_loop.py     # 端到端治理测试
├── requirements.txt
├── .github/workflows/ci.yml
├── README.md / .ja.md / .zh.md
└── LICENSE
```

---

## 🏛️ 7 层

| 层 | 回答的问题 | 范围 |
|------|-----------|------|
| **KOJIKI** | 什么存在 — 本体 | 实体、关系、7 个合并部门 |
| **SACCADE** | 尝试前问题是否恰当 | 先验、有界迭代框架（收敛或达上限） |
| **SYNAPSIS** | 单个有界决策如何产生 | 单 Bot、刚性、可审计 — Evidence ≠ Interpretation ≠ Strategy |
| **NEURAXIS** | 失败需沿抽象阶梯上溯多远才能解释 | 事后、仅实发散时升级、L3/L4 治理 |
| **MYCELIUM** | 多部门多决策如何保持协调 | 涌现 OKR 依赖图、子图级 Signal、非指令 |
| **SENTINEL** | 到底是谁说的 | 每个跨节点声明都有签名、哈希链、非同质化来源 |

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
| **LEARNING** | 提取模式 | — | 结果 vs 期望 | `learning.json` |

**`kojiki/core/runner.py` 强制的不变量：**
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

治理门控：重复阈值（N 个不同经验）、决策权利、带故障关闭默认值的 SLA。

### SENTINEL（来源证明）

| 属性 | 实现 |
|------|------|
| **签名** | Ed25519，私钥仅由节点运行时持有 |
| **非同质化** | `entry_id = hash(payload_hash + signer + prev_entry_id)` |
| **链** | 每日志（`signals.jsonl`, `edges_history.jsonl`, `gate_evidence.jsonl`） |
| **验证** | 提交前 + 治理门控计算证据前 |

### Kaizen 循环（持续改进）

| 能力 | 实现 |
|------|------|
| **问题检测** | 结果检查带护栏（完整性、方差、置信度校准） |
| **根因** | PDCA 循环带 14 类别错误分类法 |
| **重新分类** | 基于失败类型自动升级 L0→L4 |
| **治理集成** | L3/L4 变更需要门控批准 |
| **重定义捕获** | 经验包含替代 Problem 对象 |
| **学习账本** | 版本化案例、模式、规则 — 从不静默覆盖 |

### OKR Engine (BCG Methodology)

| 能力 | 实现 |
|------|------|
| **Corporate objectives** | 顶层战略，加权 KRs，灵活时间范围 |
| **Department objectives** | 从 Corporate 分解，Owner + 带状态/置信度的 KRs |
| **Team OKRs** | 参谋长自动生成，血统强制，depends_on[] |
| **进度汇总** | Team → Dept → Corporate 加权进度，成熟度评分 |
| **治理集成** | 目标变更需 L3/L4 门控，depends_on[] 阻断推进 |

### 参谋长（协调者）

| 能力 | 实现 |
|------|------|
| **目标分解** | 模式匹配 + LLM 规划 → 专家任务 |
| **专家发现** | 注册表自动发现 `specialists/<dept>/<agent>/` |
| **并行执行** | 同时运行独立专家 |
| **依赖管理** | Sales 等 Product 规格；Finance 等 Eng 估算 |
| **冲突解决** | 检测重叠决策权利；升级到治理 |
| **综合** | 合并为统一计划带统一决策权利 |

---

## 📚 研究与参考文献

架构建立在四个独立领域的同行评审研究之上：

### 生物学（菌根网络）

| 研究 | 发现 | 架构映射 |
|------|------|----------|
| Tero et al., *Science* (2010) | Physarum 强化/衰减在无中央规划者下收敛于高效、耐故障的拓扑 | MYCELIUM 强化公式、γ 效率-冗余权衡 |
| Gorzelak et al., *AoB Plants* (2015) | CMN 介导的植物通讯主流案例 | 信号传播基础 |
| Song et al., *PLoS ONE* (2010); Babikova et al. (2013) | 防御信号传播 ("priming") | 子图级 Signal 传播 |
| Karst, Jones & Hoeksema, *Nature Ecology & Evolution* (2023) | 怀疑性评论：CMN 文献中正面效应研究的引用偏差 | §II.5 警示 — 仅构建在有充分支持的机制上 |
| Frew et al., *Functional Ecology* 专刊 (2025) | CMN 是异质的，取决于语境/宿主/真菌类型 | 强化 §II.5 警示 |
| Silvestri et al. (2025), *New Phytologist* 状态报告 (2026) | AM 共生中发现新分子调节机制 (`ckRNAi`) | §II.6 — 细胞层不断证明更刚性 |
| Bilgen & Akan, "Internet of Plants" (2024–2025, Cambridge/Koç) | 独立通讯工程形式化：真菌网络作为"基于图的通讯介质" | 验证 `SIGNALING ≠ ORCHESTRATION` 不变量 (§IV.3, §II.7) |
| Adamatzky, *Royal Society Open Science* (2022) | 真菌电脉冲显示类似基础代码的统计结构 | 标记为投机性 (§II.4)，非承重 |

### 神经科学（层级预测编码）

| 研究 | 发现 | 架构映射 |
|------|------|----------|
| Rao & Ballard (1999) | 层级预测编码：预测向下，残差误差向上；误差上爬直到被吸收 | NEURAXIS 升级梯 — 完全相同的计算结构 |
| 脊髓 → 延脑 → 皮层反射弧 | 快速局部响应；模糊刺激升级；皮层抑制调节反射 | NEURAXIS L0–L4 层带 L3 治理门控 |

### 免疫学（先天/适应性免疫边界）

| 研究 | 发现 | 架构映射 |
|------|------|----------|
| 先天免疫 (TLRs, 固定) → 适应性免疫 (抗体, 记忆) | 适应性用学习层补充先天；从不重写先天识别机制 | NEURAXIS 治理门控：L0–L2 自主，L3–L4 需外部验证 |

### RL-for-LLM 研究

| 研究 | 发现 | 架构映射 |
|------|------|----------|
| 稀疏轨迹级奖励 → 过程级信用分配 | 逐步信用分配用更少数据产生更好学习 | SYNAPSIS 逐阶段分解带 `diagnosed_cause_category` 来自学习分类法 |

### 企业多 Agent 参考架构

| 来源 | 发现 | 架构映射 |
|------|------|----------|
| Microsoft 多 Agent 参考架构（真实部署） | 注册表 → 编排器 → 知识/状态 → 异步重放感知通讯 | 独立到达相同组件分离 |

### 递归自我改进分类法

| 研究 | 发现 | 架构映射 |
|------|------|----------|
| 有界 (L3) vs 无界 (L4/L5) 自我改进 | 有界：改进机制外部维护 | `LEARNING ≠ PERMISSION TO REWRITE DOCTRINE` 不变量保持系统在 L3 |

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
| **敏感性分析** | γ / decay_rate / 阈值校准 | *待定* |

完整映射：`synapsis/REFERENCES.md`  
框架复制自：`consultant/` (50+ 框架, MIT, 无 `.git`)

---

## 🛣️ 路线图

| 阶段 | 焦点 | 状态 |
|------|------|------|
| **v1** | 刚性层（SYNAPSIS）+ 涌现层（MYCELIUM）+ NEURAXIS + SENTINEL | ✅ 完成 |
| **v2** | Task 3 确定性评分、CI 带 py_compile、通过/失败阈值、Schema 版本控制、扩展演示矩阵 | 📋 计划中 |
| **v3** | 输出的对抗性重新推导、追溯改装所有 18 部门、工件交叉检查 | 📋 计划中 |

详见 `MYCELIAL-GOVERNANCE-COMPLETE-THESIS.md`。

---

## 🤝 贡献

1. **无闭源依赖** — 所有代码 MIT
2. **本地优先** — 可在本地运行，无需云端
3. **提供商无关** — 将任何 LLM 指向 `AGENT.md`
4. **必须测试** — `python3 -m py_compile` + 验证器通过
5. **仅设计时参考** — `consultant/` 是副本，非依赖

---

## 📄 许可证

MIT — 见 [LICENSE](LICENSE)。

---

## 🔗 链接

- **论文**: `MYCELIAL-GOVERNANCE-COMPLETE-THESIS.md`（双层架构、生物学、治理）
- **参考映射**: `synapsis/REFERENCES.md`
- **咨询框架**: `consultant/`（50+ 框架、斜杠命令）
- **演示**: `mycelium/examples/demo_marketing_sales.py`

---

**Kojiki Decision System. 不留未审计的决策。**