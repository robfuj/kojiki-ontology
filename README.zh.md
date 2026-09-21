# Kojiki Decision System / Kojiki 决策系统

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

### 双层设计

| 层级 | 目的 | 关键属性 |
|------|------|----------|
| **Root（刚性层）** | 单个 Bot 的内部流水线 | 强制顺序、上下文隔离、`EVALUATION ≠ ORIGINATION` |
| **Canopy（涌现层）** | Bot 间协调 | 冗余路由、相互强化、无中央控制器 |

```
┌─────────────────────────────────────────────────────────────┐
│  MYCELIUM Canopy Tier（涌现协调）                            │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │Marketing│──│  Sales  │──│Finance  │──│Engineer │  8     │
│  │  Head   │  │  Head   │  │  Head   │  │  Head   │ lines  │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
│       │            │            │            │              │
│       ▼            ▼            ▼            ▼              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │Operations│  │ Legal   │  │People & │  │Tech Plat│        │
│  │  Head   │  │  Head   │  │ Comms   │  │  Head   │        │
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

## 🏛️ 8 个合并部门

| 部门 | 范围 |
|------|------|
| **Finance** | 预算、CAC、ROI、FP&A、财务 |
| **Marketing** | 品牌、增长、推荐、付费媒体 |
| **Sales** | 外向、增长、Biz Dev、Corp Dev |
| **Engineering** | 产品、客户成功、技术、推荐技术 |
| **Operations** | 供应链、采购、日常运营 |
| **Legal** | 合规、风险、合同、监管 |
| **People & Comms** | HR、内部沟通、公共事务 |
| **Technology Platform** | AI 策略、模型、治理、InfoSec、身份、工具 |

---

## 🚀 快速开始

```bash
# 克隆决策系统
git clone <your-repo-url>
cd decision-systems

# 安装依赖
pip install -r requirements.txt

# 运行专家
python -m engine.kojiki_core.runner marketing-brand dispatch.json

# 运行所有 9 个专家（测试模式）
KOJIKI_TEST_MODE=true python tests/scripts/verify_all_runners.py
```

---

## 🤖 Orchestrator（编排器）

**Orchestrator**（替代参谋长）提供透明的目标分解：

```bash
# 运行带用户批准门控的编排
python -m engine.orchestrator.orchestrator "为加拿大市场创建牛肉汤品牌"

# 无批准门控运行（自动化用）
python -m engine.orchestrator.orchestrator "目标放这里" --no-approval
```

**流程：**
1. **Orientation Protocol** — 目标行业调研
2. **SACCADE Framing** — 将原始目标锐化为结构化问题
3. **Department Selection** — 哪些部门负责人拥有此目标，附带推理
4. **OKR Decomposition** — 企业 OKR → 部门 OKR → 团队 OKR
5. **Parallel Dispatch** — 每个部门负责人运行完整 SYNAPSIS 流水线
6. **Mycelium Coordination** — 跨部门信号
7. **User Approval Gate** — 重新循环前审查

---

## 🤖 部门子 Agent

| 部门 | 子 Agent |
|------|----------|
| Ai Intelligence | `agentic-identity`, `agents-orchestrator`, `ai-code-auditor`, `ai-engineer`, `ai-remediation`, `doc-generator`, `identity-graph`, `llm-post-training`, `mcp-builder`, `model-qa`, `multi-agent-architect`, `prompt-engineer`, `rag-pipeline`, `secrets-hygiene`, `strategy-duel`, `zk-steward` |
| Engineering Platform | `ai-engineer`, `api-engineer`, `appsec-engineer`, `backend-architect`, `code-reviewer`, `data-viz`, `database-optimizer`, `devops-automator`, `frontend-developer`, `llm-post-training`, `multi-agent-architect`, `platform-engineer`, `rag-engineer`, `reality-checker`, `security-architect`, `software-architect`, `sre`, `test-automation` |
| Finance Accounting | `accounts-payable`, `bookkeeper`, `cfo`, `esg-officer`, `financial-analyst`, `fp-a-analyst`, `grant-writer`, `investment-researcher`, `loan-officer`, `medical-billing`, `pricing-analyst`, `tax-strategist` |
| Legal Compliance | `compliance-auditor`, `data-privacy`, `esg-officer`, `fedramp`, `gov-presales`, `legal-billing`, `legal-client-intake`, `legal-doc-review` |
| Marketing Brand | `aeo-specialist`, `agentic-search-optimizer`, `brand-guardian`, `carousel-growth`, `content-creator`, `email-strategist`, `growth-hacker`, `paid-social-specialist`, `pr-communications`, `seo-specialist`, `video-optimizer`, `visual-storyteller` |
| Operations Ops | `business-strategist`, `change-management`, `ma-integration`, `operations-manager`, `supply-chain-strategist` |
| People Hr | `change-management`, `corporate-training`, `customer-service`, `customer-success`, `dev-advocate`, `hr-onboarding`, `org-psychologist`, `pr-comms`, `recruitment`, `support-responder` |
| Sales Outbound | `account-strategist`, `data-consolidation`, `deal-strategist`, `discovery-coach`, `lead-gen-strategist`, `outbound-strategist`, `pipeline-analyst`, `proposal-strategist`, `report-distribution`, `sales-coach`, `sales-data-extraction`, `sales-engineer`, `sales-outreach`, `salesforce-architect` |

**总计：8 部门 95 个子 Agent**

---

## 🔍 Orientation Protocol — 基于研究的目标澄清

**目的：** 在任何部门选择或规划之前，系统运行**自适应、研究优先的定向**，防止对模糊目标的浪费性研究（如"提升 Q4 销售" → 研究适配为"SaaS B2B 管道加速"）。

### 流程

```
CLARIFYING QUESTIONS (2–4 自适应) 
    → LIVE WEB RESEARCH (market, competitors, regulation, risks)
    → RESEARCH BRIEF + CONTEXTUAL FOLLOW-UPS (3–4 从发现生成)
    → USER ANSWERS
    → OPTIONAL: TARGETED RE-RESEARCH (若答案揭示缺口) + MORE FOLLOW-UPS
    → REFINED GOAL → DEPARTMENT SELECTION → OKR DECOMPOSITION
```

### 为什么研究优先？

- **Clarifying questions** 使目标足够具体以进行*目标*研究
- **Live research** 将跟进建立在当前现实中（而非陈旧模板）
- **Follow-ups generated FROM findings** —— 而非静态问题库
- **Re-research loop** 捕捉用户回答打开的缺口

### 示例（来自 Vercel 流程）

```
Goal: "Launch gacha game"
Research finds: Belgium/Netherlands ban loot boxes; EU Digital Fairness Act pending
Follow-up Q1: "What is the launch-country sequence — soft-launch EU before UK/BE/NL?"
Follow-up Q2: "Does monetization need odds disclosure + spending controls for EU compliance?"
Follow-up Q3: "What revenue threshold defines FY27 launch success?"
```

### 提问技巧研究（开源基础）

| Source | Key Finding | Applied In |
|--------|-------------|------------|
| **Cognitive Interviewing Guide** (UCLA/Chime) | 开放式、非引导性问题减少回忆偏见；"发生了什么？" > "X 发生了吗？" | 澄清阶段："具体涉及什么？" |
| **Oxford Handbook of Survey Methodology** (2018) | 漏斗序列：宽泛→具体；避免双管问题 | Phase 1 → Phase 3 收窄 |
| **Karpathy's LLM Wiki / Akinator-style entropy** | 通过信息增益自适应选择问题；熵 < 阈值时停止 | 动态问题数量 (2–4) |
| **Deep Research pattern** (OpenAI/Perplexity) | 迭代：澄清→搜索→综合→跟进→再搜索 | 3 阶段定向循环 |
| **Police PEACE model / CI guidelines** | 回忆前情境恢复；特定探询前自由叙述 | "最近发生什么让这成为优先事项？" |

---

## 🧠 MORPHEUS Protocol — 带 SENTINEL 验证的每日内存重置

**目的：** 通过强制执行每日 **Hibernate → Hypnos → Morpheus → Awaken** 循环，防止长期运行编排中的记忆漂移，该循环通过加密方式验证没有遗漏待处理门控或活跃 SLA。

| 阶段 | 行动 | SENTINEL 检查 |
|------|------|--------------|
| **Hibernate** | 工作存储快照（经验、kaizen、子图边） | 哈希写入链 |
| **Hypnos** | 封印快照——标记重置条目 | 签名检查点 |
| **Morpheus** | 擦除工作存储；重现带有实时 SLA 截止日期的门控 | 查询真实门控存储 (`escalation_engine.gate_requests`) |
| **Awaken** | 验证链完整性；确认待处理门控已恢复 | 哈希不匹配则 fail-closed |

**关键保证：**
- 任何具有实时 SLA 截止日期的门控都能在擦除中幸存（从真实存储查询，而非存根）
- 链验证是强制的——如果来源链断裂，编排无法恢复
- 测试套件中验证了 7/7 接受标准

---

## 🔄 提示词如何流经系统

### 1. 入口点：Dispatch 创建

```python
dispatch = {
    "task_id": "verify-marketing-brand",
    "raw_record": "Test goal for verification",
    "raw_source": {},
    "prior_accepted_evidence": []
}
```

Dispatch 是不可变的输入契约。包含原始目标、任何源数据和先前证据。

### 2. 流水线初始化 (`engine/kojiki_core/runner.py`)

```python
specialist = load_specialist("marketing-brand")
runner = PipelineRunner(specialist, dispatch)
```

`PipelineRunner`：
- 加载专家配置（阶段、模式、工具、验证器）
- 创建用于上下文隔离的 `ScopedContext`
- 为 SENTINEL 来源初始化 `CausalChainRunner`
- 为 Decision Rights 加载注册表

### 3. 阶段执行循环

运行器按严格顺序执行阶段：

```python
STAGE_EXECUTORS = [
    ("saccade", run_saccade_stage),
    ("evidence", run_evidence_stage),
    ("interpretation", run_interpretation_stage),
    ("strategy", run_strategy_stage),
    ("output", run_output_stage),
    ("delegation", run_delegation_stage),
    ("handoff", run_handoff_stage),
    ("mycelium", run_mycelium_stage),
    ("outcome", run_outcome_stage),
    ("learning", run_learning_stage),
]
```

**每个阶段执行遵循此模式：**

1. 从专家获取 **StageConfig**（提示词、工具、模式、允许输入）
2. **构建作用域上下文**——仅来自 dispatch + 先前阶段输出的 `inputs_allowed` 键
3. 从文件**加载提示词**
4. 通过 `call_model()` **调用模型**（测试模式存根，生产环境真实 LLM）
4. **针对 JSON Schema 验证输出**
5. **存入上下文**供下游阶段使用
6. **记录因果链**用于 SENTINEL 来源

### 4. 阶段详细拆解

| 阶段 | 目的 | 输出 | 权限 |
|------|---------|------|--------|
| **SACCADE** | 先验问题框架 | 结构化问题 | 绝不可变成 EVIDENCE 或 STRATEGY |
| **EVIDENCE** | 来源检索 | 带引用的发现 | 绝不可变成 INTERPRETATION 或 STRATEGY |
| **INTERPRETATION** | 证据综合 | 诊断 + 洞察 | 绝不可变成 EVIDENCE 或 STRATEGY |
| **STRATEGY** | 决策计划 | 目标 + 决策权 | 绝不可变成 EVIDENCE 或 INTERPRETATION |
| **OUTPUT** | 干预设计 | 战术 + 度量 | 绝不可变成 EVIDENCE/INTERPRETATION/STRATEGY |
| **DELEGATION** | 子 Agent 派遣 | 任务分配 | — |
| **HANDOFF** | 跨 Agent 协调 | 交接追踪 | — |
| **MYCELIUM** | 信号传播 | 跨部门信号 | — |
| **OUTCOME** | Kaizen 评估 | 分数 + 收敛 | — |
| **LEARNING** | Kaizen 综合 | 模式 + 重定义 | — |

### 关键不变量

- `EVIDENCE ≠ INTERPRETATION ≠ STRATEGY`（无渗漏）
- `LEARNING ≠ PERMISSION TO REWRITE DOCTRINE`（有界 L3）
- `SIGNALING ≠ ORCHESTRATION`（冠层自主性）

---

## 📁 仓库结构

```
decision-systems/
├── engine/                          # 所有引擎模块
│   ├── kojiki_core/                 # 核心 SYNAPSIS 流水线
│   ├── mycelium/                    # 水平信号传播
│   ├── neuraxis/                    # 垂直升级引擎 (L0–L4)
│   ├── kaizen/                      # 学习循环 (PDCA)
│   ├── sentinel/                    # 来源：Ed25519、哈希链日志
│   └── synapsis/                    # 因果链、Schema、验证
├── tests/
│   ├── engine/                      # 按引擎组件组织的测试
│   ├── fixtures/                    # 测试数据
│   ├── integration/                 # 集成测试
│   ├── scripts/                     # 验证脚本
│   ├── unit/                        # 单元测试
│   └── results/                     # 测试输出产物
├── skills/                          # Agent 技能
├── bots/                            # 参考 Bot
├── vendor/                          # 外部引用（顾问框架）
├── var/                             # 运行时数据 (gitignored)
├── mycelium_data/                   # 运行时数据（从 mycelium/ 重命名）
├── ui/                              # Next.js 前端
├── api_server.py                    # FastAPI 后端
├── requirements.txt
└── README.md / .ja.md / .zh.md
```

---

## 🧪 测试

```bash
# 验证所有 9 个专家（测试模式）
KOJIKI_TEST_MODE=true python tests/scripts/verify_all_runners.py

# 运行 Mycelium 测试（42 个测试）
PYTHONPATH=. python -m pytest tests/engine/mycelium/ -v

# 运行治理循环测试
python -m pytest tests/integration/test_governance_loop.py -v
```

**所有测试通过：**
- ✅ 9/9 专家通过验证
- ✅ 42/42 Mycelium 测试通过
- ✅ 治理循环测试通过

---

## 🔬 研究基础

架构建立在六个独立领域的同行评审研究之上：

### 生物学（菌根网络）

| 研究 | 发现 | 架构映射 |
|------|---------|---------------------|
| Tero et al., *Science* (2010) | Physarum 强化/衰减在无中央规划者下收敛于高效、耐故障的拓扑 | MYCELIUM 强化公式、γ 效率-冗余权衡 |
| Gorzelak et al., *AoB Plants* (2015) | CMN 介导的植物通讯主流案例 | 信号传播基础 |
| Song et al., *PLoS ONE* (2010); Babikova et al. (2013) | 防御信号传播 ("priming") | 子图级 Signal 传播 |
| Karst et al., *Nature Ecology & Evolution* (2023) | 怀疑性评论：引用偏向正面效应研究 | §II.5 警示 —— 仅构建有充分支持的机制 |
| Frew et al., *Functional Ecology* (2025) | CMN 是异质的、依赖语境/宿主/真菌类型 | 强化 §II.5 警示 |
| Bilgen & Akan, "Internet of Plants" (2024–2025) | 独立通信工程形式化：真菌网络作为"基于图的通信媒介" | 验证 `SIGNALING ≠ ORCHESTRATION` 不变量 |

### 神经科学（层级预测编码）

| 研究 | 发现 | 架构映射 |
|------|---------|---------------------|
| Rao & Ballard (1999) | 层级预测编码：预测向下，残差误差向上；误差上爬直到被吸收 | NEURAXIS 升级梯 —— 完全相同的计算结构 |
| 脊髓 → 延髓 → 皮层反射弧 | 快速局部响应；模糊刺激升级；皮层抑制调节反射 | NEURAXIS L0–L4 层带 L3 治理门控 |

### 免疫学（先天/适应性免疫边界）

| 研究 | 发现 | 架构映射 |
|------|---------|---------------------|
| 先天免疫 (TLRs, 固定) → 适应性免疫 (抗体, 记忆) | 适应性用学习层补充先天；从不重写先天识别机制 | NEURAXIS 治理门控：L0–L2 自主，L3–L4 需外部验证 |

### RL-for-LLM 研究

| 研究 | 发现 | 架构映射 |
|------|---------|---------------------|
| 稀疏轨迹级奖励 → 过程级信用分配 | 逐步信用分配用更少数据产生更好学习 | SYNAPSIS 逐阶段分解带 `diagnosed_cause_category` 来自学习分类法 |

### 企业多 Agent 参考架构

| 来源 | 发现 | 架构映射 |
|------|---------|---------------------|
| Microsoft 多 Agent 参考架构（真实部署） | 注册表 → 编排器 → 知识/状态 → 异步重放感知通讯 | 独立到达相同组件分离 |

### 递归自我改进分类学

| 研究 | 发现 | 架构映射 |
|------|---------|---------------------|
| 有界 (L3) vs 无界 (L4/L5) 自我改进 | 有界：改进机制外部维护 | `LEARNING ≠ PERMISSION TO REWRITE DOCTRINE` 不变量保持系统在 L3 |

---

## 📄 许可证

MIT — 见 [LICENSE](LICENSE)。

---

## 🔗 链接

- **论文**: `MYCELIAL-GOVERNANCE-COMPLETE-THESIS.md`（双层架构、生物学、治理）
- **参考映射**: `engine/synapsis/REFERENCES.md`
- **咨询框架**: `vendor/consultant/` (50+ 框架)

---

## 🤖 部门子 Agent

| 部门 | 子 Agent |
|------|----------|
| Ai Intelligence | `agentic-identity`, `agents-orchestrator`, `ai-code-auditor`, `ai-engineer`, `ai-remediation`, `doc-generator`, `identity-graph`, `llm-post-training`, `mcp-builder`, `model-qa`, `multi-agent-architect`, `prompt-engineer`, `rag-pipeline`, `secrets-hygiene`, `strategy-duel`, `zk-steward` |
| Engineering Platform | `ai-engineer`, `api-engineer`, `appsec-engineer`, `backend-architect`, `code-reviewer`, `data-viz`, `database-optimizer`, `devops-automator`, `frontend-developer`, `llm-post-training`, `multi-agent-architect`, `platform-engineer`, `rag-engineer`, `reality-checker`, `security-architect`, `software-architect`, `sre`, `test-automation` |
| Finance Accounting | `accounts-payable`, `bookkeeper`, `cfo`, `esg-officer`, `financial-analyst`, `fp-a-analyst`, `grant-writer`, `investment-researcher`, `loan-officer`, `medical-billing`, `pricing-analyst`, `tax-strategist` |
| Legal Compliance | `compliance-auditor`, `data-privacy`, `esg-officer`, `fedramp`, `gov-presales`, `legal-billing`, `legal-client-intake`, `legal-doc-review` |
| Marketing Brand | `aeo-specialist`, `agentic-search-optimizer`, `brand-guardian`, `carousel-growth`, `content-creator`, `email-strategist`, `growth-hacker`, `paid-social-specialist`, `pr-communications`, `seo-specialist`, `video-optimizer`, `visual-storyteller` |
| Operations Ops | `business-strategist`, `change-management`, `ma-integration`, `operations-manager`, `supply-chain-strategist` |
| People Hr | `change-management`, `corporate-training`, `customer-service`, `customer-success`, `dev-advocate`, `hr-onboarding`, `org-psychologist`, `pr-comms`, `recruitment`, `support-responder` |
| Sales Outbound | `account-strategist`, `data-consolidation`, `deal-strategist`, `discovery-coach`, `lead-gen-strategist`, `outbound-strategist`, `pipeline-analyst`, `proposal-strategist`, `report-distribution`, `sales-coach`, `sales-data-extraction`, `sales-engineer`, `sales-outreach`, `salesforce-architect` |

**总计：8 部门 95 个子 Agent**

---

**Kojiki Decision System. 不留未审计的决策。**