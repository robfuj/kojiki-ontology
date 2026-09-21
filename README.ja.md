# Kojiki Decision System / Kojiki 意思決定システム

**ローカルファーストのオープンソースフレームワークで、任意のLLMを意思決定中心の組織に変換します。**

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![Tests Passing](https://img.shields.io/badge/Tests-All%20Passing-brightgreen.svg)](#testing)

---

## 🌐 Language / 言語 / 语言

[**English**](README.md) • [**日本語**](README.ja.md) • [**中文**](README.zh.md)

---

## 🎯 これは何ですか？

Kojikiは、任意のLLM（Claude、GPT、ローカルモデル、エージェントハーネス）に**共有・監査可能な意思決定構造**を与えます——単なるチャットではありません。すべての部門エージェントが同じ**SYNAPSIS変換チェーン**を通じて推論します：

```
RECORD → SACCADE → EVIDENCE → INTERPRETATION → STRATEGY → OUTPUT → OUTCOME → LEARNING
```

各ステージは**境界付き変換**であり、明示的な権限と「黙って何かに変わってはいけないもの」があります。**Brain**が統括し、独立した**Adversarial Audit**が異議を唱えます。部門横断の調整は**MYCELIUMキャノピー層**で行われます——菌根ネットワークをモデルにした分散型・ニーズ駆動の基盤です。

> **「現在」は安価な部分です。** なぜその意思決定がなされたのか——どの証拠が支持し、どの仮定が失敗し、ガバナンスゲートが何を要求したのか——をトレースしようとした瞬間、その構造が元を取ります。

---

## 🏗️ アーキテクチャ概要

### 二層設計

| 層 | 目的 | 主な特性 |
|------|---------|--------------|
| **Root（剛性）** | 単一スペシャリストの内部パイプライン | 順序強制、コンテキスト隔離、`EVALUATION ≠ ORIGINATION` |
| **Canopy（創発）** | スペシャリスト横断の調整 | 冗長ルーティング、相互強化、中央コントローラなし |

```
┌─────────────────────────────────────────────────────────────┐
│  MYCELIUM Canopy Tier（創発調整）                            │
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
│  SYNAPSIS Root Tier（各スペシャリストの剛性パイプライン）        │
│  RECORD → SACCADE → EVIDENCE → INTERPRETATION → STRATEGY    │
│       → OUTPUT → OUTCOME → LEARNING                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │Runner.py│  │Schema   │  │Adversary│  │Brain    │        │
│  │context  │  │validate │  │Audit    │  │adjudicate│        │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### 三つの垂直軸

| 軸 | コンポーネント | 目的 |
|------|-----------|---------|
| **水平** | MYCELIUM | 部門横断調整（OKR基盤） |
| **垂直** | NEURAXIS | 再帰的問題再定義（L0–L4エスカレーション） |
| **アプリオリ** | SACCADE | 証拠収集前の問題フレーミング |

### 由来層（SENTINEL）

全ての信号、エッジ変更、ゲート証拠は**非代替性、ハッシュチェーン、Ed25519署名付き由来トークン**でラップされます——ガバナンスゲートの「N個の異なる経験」基準が、捏造された主張ではなく*検証済み*裏付けを数えます。

---

## 🏛️ 8つの統合部門

| 部門 | 範囲 |
|------------|-------|
| **Finance** | 予算、CAC、ROI、FP&A、財務 |
| **Marketing** | ブランド、成長、紹介、有料メディア |
| **Sales** | アウトバウンド、成長、Biz Dev、Corp Dev |
| **Engineering** | 製品、カスタマーサクセス、テクノロジー、紹介技術 |
| **Operations** | サプライチェーン、調達、日常運用 |
| **Legal** | コンプライアンス、リスク、契約、規制 |
| **People & Comms** | HR、社内コミュニケーション、広報 |
| **Technology Platform** | AI戦略、モデル、ガバナンス、InfoSec、アイデンティティ、ツール |

---

## 🚀 クイックスタート

```bash
# 依存関係をインストール
pip install -r requirements.txt

# スペシャリストを実行（テストモード）
KOJIKI_TEST_MODE=true python -m engine.kojiki_core.runner marketing-brand dispatch.json

# 全9スペシャリストを実行（テストモード）
KOJIKI_TEST_MODE=true python tests/scripts/verify_all_runners.py
```

---

## 🤖 Orchestrator（オーケストレーター）

**Orchestrator**が透過的な目標分解を提供：

```bash
# ユーザー承認ゲート付きで実行
python -m engine.orchestrator.orchestrator "カナダ市場向けビーフブロスブランドを作成"

# 承認ゲートなしで実行（自動化用）
python -m engine.orchestrator.orchestrator "目標をここに" --no-approval
```

**フロー：**
1. **Orientation Protocol** — 目標に関する業界調査
2. **SACCADE Framing** — 生目標を構造化された問題に研ぎ澄ます
3. **Department Selection** — どの部門長が担当か、理由付きで決定
4. **OKR Decomposition** — 企業OKR → 部門OKR → チームOKR
5. **Parallel Dispatch** — 各部門長が完全SYNAPSISパイプラインを実行
6. **Mycelium Coordination** — 部門横断シグナル
7. **User Approval Gate** — 再ループ前のレビュー

---

## 🤖 部門別サブエージェント

| 部門 | サブエージェント |
|------------|------------|
| Ai Intelligence | `agentic-identity`, `agents-orchestrator`, `ai-code-auditor`, `ai-engineer`, `ai-remediation`, `doc-generator`, `identity-graph`, `llm-post-training`, `mcp-builder`, `model-qa`, `multi-agent-architect`, `prompt-engineer`, `rag-pipeline`, `secrets-hygiene`, `strategy-duel`, `zk-steward` |
| Engineering Platform | `ai-engineer`, `api-engineer`, `appsec-engineer`, `backend-architect`, `code-reviewer`, `data-viz`, `database-optimizer`, `devops-automator`, `frontend-developer`, `llm-post-training`, `multi-agent-architect`, `platform-engineer`, `rag-engineer`, `reality-checker`, `security-architect`, `software-architect`, `sre`, `test-automation` |
| Finance Accounting | `accounts-payable`, `bookkeeper`, `cfo`, `esg-officer`, `financial-analyst`, `fp-a-analyst`, `grant-writer`, `investment-researcher`, `loan-officer`, `medical-billing`, `pricing-analyst`, `tax-strategist` |
| Legal Compliance | `compliance-auditor`, `data-privacy`, `esg-officer`, `fedramp`, `gov-presales`, `legal-billing`, `legal-client-intake`, `legal-doc-review` |
| Marketing Brand | `aeo-specialist`, `agentic-search-optimizer`, `brand-guardian`, `carousel-growth`, `content-creator`, `email-strategist`, `growth-hacker`, `paid-social-specialist`, `pr-communications`, `seo-specialist`, `video-optimizer`, `visual-storyteller` |
| Operations Ops | `business-strategist`, `change-management`, `ma-integration`, `operations-manager`, `supply-chain-strategist` |
| People Hr | `change-management`, `corporate-training`, `customer-service`, `customer-success`, `dev-advocate`, `hr-onboarding`, `org-psychologist`, `pr-comms`, `recruitment`, `support-responder` |
| Sales Outbound | `account-strategist`, `data-consolidation`, `deal-strategist`, `discovery-coach`, `lead-gen-strategist`, `outbound-strategist`, `pipeline-analyst`, `proposal-strategist`, `report-distribution`, `sales-coach`, `sales-data-extraction`, `sales-engineer`, `sales-outreach`, `salesforce-architect` |

**合計: 8部門で95サブエージェント**

---

## 🔍 Orientation Protocol — 研究に基づく目標明確化

**目的:** 部門選択や計画の前に、システムが**適応的・研究優先のオリエンテーション**を実行し、曖昧な目標への無駄な調査を防ぎます（例: 「Q4売上を上げる」→ 研究が「SaaS B2Bパイプライン加速」に適応）。

### フロー

```
CLARIFYING QUESTIONS (2–4 adaptive) 
    → LIVE WEB RESEARCH (market, competitors, regulation, risks)
    → RESEARCH BRIEF + CONTEXTUAL FOLLOW-UPS (3–4 generated FROM findings)
    → USER ANSWERS
    → OPTIONAL: TARGETED RE-RESEARCH (if answers reveal gaps) + MORE FOLLOW-UPS
    → REFINED GOAL → DEPARTMENT SELECTION → OKR DECOMPOSITION
```

### なぜ研究優先か？

- **Clarifying questions** で目標を *targeted* 研究に十分具体化
- **Live research** でフォローアップを現在の現実に接地（古いテンプレートではない）
- **Findings FROM generated follow-ups** — 静的な質問バンクではない
- **Re-research loop** でユーザー回答が開くギャップを検出

### 例（Vercelフローから）

```
Goal: "Launch gacha game"
Research finds: Belgium/Netherlands ban loot boxes; EU Digital Fairness Act pending
Follow-up Q1: "What is the launch-country sequence — soft-launch EU before UK/BE/NL?"
Follow-up Q2: "Does monetization need odds disclosure + spending controls for EU compliance?"
Follow-up Q3: "What revenue threshold defines FY27 launch success?"
```

### 良い質問をするための研究（オープンソース基盤）

| Source | Key Finding | Applied In |
|--------|-------------|------------|
| **Cognitive Interviewing Guide** (UCLA/Chime) | Open-ended, non-leading questions reduce recall bias; "What happened?" > "Did X happen?" | Clarifying phase: "What specifically does that involve?" |
| **Oxford Handbook of Survey Methodology** (2018) | Funnel sequence: broad → specific; avoid double-barreled questions | Phase 1 → Phase 3 narrowing |
| **Karpathy's LLM Wiki / Akinator-style entropy** | Adaptive question selection via information gain; stop when entropy < threshold | Dynamic question count (2–4) |
| **Deep Research pattern** (OpenAI/Perplexity) | Iterative: clarify → search → synthesize → follow-up → re-search | 3-phase orientation loop |
| **Police PEACE model / CI guidelines** | Context reinstatement before recall; free narrative before specific probes | "What happened recently that made this a priority?" |

---

## 🧠 MORPHEUS Protocol — SENTINEL検証付き日次メモリリセット

**目的:** 長時間実行オーケストレーションでのメモリドリフトを防ぐため、**Hibernate → Hypnos → Morpheus → Awaken** の日次サイクルを暗号学的に強制し、保留中のゲートやアクティブなSLAが失われないことを検証。

| フェーズ | アクション | SENTINELチェック |
|-------|--------|----------------|
| **Hibernate** | 作業ストアのスナップショット（経験、kaizen、サブグラフエッジ） | ハッシュをチェーンに書き込み |
| **Hypnos** | スナップショットを封印 — リセットエントリをマーク | 署名済みチェックポイント |
| **Morpheus** | 作業ストアをワイプ; ライブSLA期限付きゲートを再物質化 | 実ゲートストアをクエリ (`escalation_engine.gate_requests`) |
| **Awaken** | チェーン整合性を検証; 保留ゲートの復元を確認 | Fail-closed if hash mismatch |

**主要保証:**
- ライブSLA期限を持つゲートはワイプ後も生存（実ストアからクエリ、スタブではない）
- チェーン検証は必須 — 由来が壊れていればオーケストレーション再開不可
- テストスイートで7/7の受入基準を検証済み

---

## 🔄 プロンプトがシステムを流れる仕組み

### 1. エントリポイント: Dispatch作成

```python
dispatch = {
    "task_id": "verify-marketing-brand",
    "raw_record": "Test goal for verification",
    "raw_source": {},
    "prior_accepted_evidence": []
}
```

Dispatchは不変の入力契約。生目標、ソースデータ、過去の証拠を含む。

### 2. パイプライン初期化 (`engine/kojiki_core/runner.py`)

```python
specialist = load_specialist("marketing-brand")
runner = PipelineRunner(specialist, dispatch)
```

`PipelineRunner`:
- スペシャリスト設定（ステージ、スキーマ、ツール、バリデータ）をロード
- コンテキスト隔離用 `ScopedContext` を作成
- SENTINEL由来用 `CausalChainRunner` を初期化
- Decision Rights用レジストリをロード

### 3. ステージ実行ループ

ランナーは厳密な順序でステージを実行:

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

**各ステージ実行パターン:**
1. スペシャリストから **StageConfig** 取得（プロンプト、ツール、スキーマ、許可入力）
2. **スコープ付きコンテキスト構築** — dispatch + 過去ステージ出力から `inputs_allowed` キーのみ
3. ファイルから **プロンプト読み込み**
4. `call_model()` で **モデル呼び出し** （テストモードはスタブ、本番は実LLM）
5. JSONスキーマで **出力検証**
6. 下流ステージ用 **コンテキストに格納**
7. SENTINEL由来用 **因果チェーンに記録**

### 4. ステージ別内訳

| ステージ | 目的 | 出力 | 権限 |
|-------|---------|--------|-----------|
| **SACCADE** | アプリオリ問題フレーミング | 構造化された問題 | Must NOT become EVIDENCE or STRATEGY |
| **EVIDENCE** | ソース検索 | 引用付き発見事項 | Must NOT become INTERPRETATION or STRATEGY |
| **INTERPRETATION** | 証拠合成 | 診断 + インサイト | Must NOT become EVIDENCE or STRATEGY |
| **STRATEGY** | 意思決定計画 | 目的 + 決定権 | Must NOT become EVIDENCE or INTERPRETATION |
| **OUTPUT** | 介入設計 | 戦術 + 測定 | Must NOT become EVIDENCE/INTERPRETATION/STRATEGY |
| **DELEGATION** | サブエージェント派遣 | タスク割り当て | — |
| **HANDOFF** | エージェント間連携 | ハンドオフ追跡 | — |
| **MYCELIUM** | 信号伝播 | 部門横断シグナル | — |
| **OUTCOME** | 改善評価 | スコア + 収束 | — |
| **LEARNING** | 改善合成 | パターン + 再定義 | — |

### キー不変条件

- `EVIDENCE ≠ INTERPRETATION ≠ STRATEGY`（混入なし）
- `LEARNING ≠ PERMISSION TO REWRITE DOCTRINE`（有界L3）
- `SIGNALING ≠ ORCHESTRATION`（キャノピー自律）

---

## 📁 リポジトリ構造

```
decision-systems/
├── engine/                          # 全エンジンモジュール
│   ├── kojiki_core/                 # コアSYNAPSISパイプライン
│   ├── mycelium/                    # 水平信号伝播
│   ├── neuraxis/                    # 垂直エスカレーションエンジン（L0–L4）
│   ├── kaizen/                      # 学習ループ（PDCA）
│   ├── sentinel/                    # 由来：Ed25519、ハッシュチェーンログ
│   └── synapsis/                    # 因果チェーン、スキーマ、検証
├── tests/
│   ├── engine/                      # エンジンコンポーネント別テスト
│   ├── fixtures/                    # テストデータ
│   ├── integration/                 # 統合テスト
│   ├── scripts/                     # 検証スクリプト
│   ├── unit/                        # 単体テスト
│   └── results/                     # テスト出力成果物
├── skills/                          # エージェントスキル
├── bots/                            # 参照ボット
├── vendor/                          # 外部参照（コンサルティングフレームワーク）
├── var/                             # 実行時データ（gitignore）
├── mycelium_data/                   # 実行時データ（mycelium/から改名）
├── ui/                              # Next.jsフロントエンド
├── api_server.py                    # FastAPIバックエンド
├── requirements.txt
└── README.md / .ja.md / .zh.md
```

---

## 🧪 テスト

```bash
# 全9スペシャリストを検証（テストモード）
KOJIKI_TEST_MODE=true python tests/scripts/verify_all_runners.py

# Myceliumテスト実行（42テスト）
PYTHONPATH=. python -m pytest tests/engine/mycelium/ -v

# ガバナンスループテスト実行
python -m pytest tests/integration/test_governance_loop.py -v
```

**全テスト通過:**
- ✅ 9/9 スペシャリストが検証通過
- ✅ 42/42 Myceliumテスト通過
- ✅ ガバナンスループテスト通過

---

## 🔬 研究基盤

アーキテクチャは6つの独立分野の査読済み研究に基づく：

### 生物学（菌根ネットワーク）

| 研究 | 発見 | アーキテクチャマッピング |
|-------|---------|---------------------|
| Tero et al., *Science* (2010) | Physarum強化/減衰が中央プランナーなしで効率的・耐障害トポロジーに収束 | MYCELIUM強化公式、γ効率-冗長性トレードオフ |
| Gorzelak et al., *AoB Plants* (2015) | CMN媒介植物通信の主流事例 | 信号伝播の基盤 |
| Song et al., *PLoS ONE* (2010); Babikova et al. (2013) | 防衛信号伝播（"priming"） | スコープ付きサブグラフのみSignal伝播 |
| Karst et al., *Nature Ecology & Evolution* (2023) | 懐疑的レビュー：正の効果研究への引用バイアス | §II.5での警告——十分支持されたメカニズムのみ構築 |
| Frew et al., *Functional Ecology* (2025) | CMNsは異質、文脈/宿主/真菌タイプ依存 | §II.5の警告を強化 |
| Bilgen & Akan, "Internet of Plants" (2024–2025) | 独立通信工学形式化：菌根ネットワークを"グラフベース通信媒質"として | `SIGNALING ≠ ORCHESTRATION` 不変量を検証 |

### 神経科学（階層的予測符号化）

| 研究 | 発見 | アーキテクチャマッピング |
|-------|---------|---------------------|
| Rao & Ballard (1999) | 階層的予測符号化：予測は下向き、残差誤差は上向き；誤差は吸収されるまで登る | NEURAXISエスカレーション梯子——完全同一の計算構造 |
| 脊髄→延髄→皮質反射弧 | 高速局所応答；曖昧刺激はエスカレート；皮質抑制が反射を調節 | NEURAXIS L0–L4層、L3にガバナンスゲート |

### 免疫学（先天/適応免疫境界）

| 研究 | 発見 | アーキテクチャマッピング |
|-------|---------|---------------------|
| 先天免疫 (TLRs, 固定) → 適応免疫 (抗体, 記憶) | 適応免疫は学習層で先天を補完；先天認識機構を決して書き換えない | NEURAXISガバナンスゲート：L0–L2自律、L3–L4要外部検証 |

### RL-for-LLM研究

| 研究 | 発見 | アーキテクチャマッピング |
|-------|---------|---------------------|
| 疎軌道レベル報酬→プロセスレベル信用割当 | ステップごとの信用割当が少ないデータでより良い学習を生成 | SYNAPSIS段階ごと分解、`diagnosed_cause_category`付き（学習分類法由来） |

### エンタープライズマルチAgent参照アーキテクチャ

| ソース | 発見 | アーキテクチャマッピング |
|--------|---------|---------------------|
| MicrosoftマルチAgent参照アーキテクチャ（実配備） | レジストリ→オーケストレータ→知識/状態→非同期リプレイ感知通信 | 独立して同一コンポーネント分離に到達 |

### 再帰的自己改善分類学

| 研究 | 発見 | アーキテクチャマッピング |
|-------|---------|---------------------|
| 有界 (L3) vs 無界 (L4/L5) 自己改善 | 有界：改善機構は外部維持 | `LEARNING ≠ PERMISSION TO REWRITE DOCTRINE` 不変量でシステムをL3に維持 |

---

## 📄 ライセンス

MIT — 詳細は [LICENSE](LICENSE) を参照。

---

## 🔗 リンク

- **論文**: `MYCELIAL-GOVERNANCE-COMPLETE-THESIS.md` (二層アーキテクチャ、生物学、ガバナンス)
- **参照マッピング**: `engine/synapsis/REFERENCES.md`
- **コンサルティングフレームワーク**: `vendor/consultant/` (50+ フレームワーク)

---

## 🤖 部門別サブエージェント

| 部門 | サブエージェント |
|------------|------------|
| Ai Intelligence | `agentic-identity`, `agents-orchestrator`, `ai-code-auditor`, `ai-engineer`, `ai-remediation`, `doc-generator`, `identity-graph`, `llm-post-training`, `mcp-builder`, `model-qa`, `multi-agent-architect`, `prompt-engineer`, `rag-pipeline`, `secrets-hygiene`, `strategy-duel`, `zk-steward` |
| Engineering Platform | `ai-engineer`, `api-engineer`, `appsec-engineer`, `backend-architect`, `code-reviewer`, `data-viz`, `database-optimizer`, `devops-automator`, `frontend-developer`, `llm-post-training`, `multi-agent-architect`, `platform-engineer`, `rag-engineer`, `reality-checker`, `security-architect`, `software-architect`, `sre`, `test-automation` |
| Finance Accounting | `accounts-payable`, `bookkeeper`, `cfo`, `esg-officer`, `financial-analyst`, `fp-a-analyst`, `grant-writer`, `investment-researcher`, `loan-officer`, `medical-billing`, `pricing-analyst`, `tax-strategist` |
| Legal Compliance | `compliance-auditor`, `data-privacy`, `esg-officer`, `fedramp`, `gov-presales`, `legal-billing`, `legal-client-intake`, `legal-doc-review` |
| Marketing Brand | `aeo-specialist`, `agentic-search-optimizer`, `brand-guardian`, `carousel-growth`, `content-creator`, `email-strategist`, `growth-hacker`, `paid-social-specialist`, `pr-communications`, `seo-specialist`, `video-optimizer`, `visual-storyteller` |
| Operations Ops | `business-strategist`, `change-management`, `ma-integration`, `operations-manager`, `supply-chain-strategist` |
| People Hr | `change-management`, `corporate-training`, `customer-service`, `customer-success`, `dev-advocate`, `hr-onboarding`, `org-psychologist`, `pr-comms`, `recruitment`, `support-responder` |
| Sales Outbound | `account-strategist`, `data-consolidation`, `deal-strategist`, `discovery-coach`, `lead-gen-strategist`, `outbound-strategist`, `pipeline-analyst`, `proposal-strategist`, `report-distribution`, `sales-coach`, `sales-data-extraction`, `sales-engineer`, `sales-outreach`, `salesforce-architect` |

**合計: 8部門で95サブエージェント**

---

**Kojiki Decision System. どの意思決定も監査漏れなし。**