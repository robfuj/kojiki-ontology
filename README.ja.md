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

各ステージは**境界付き変換**であり、明示的な権限と「黙ってはならないもの」（evidence ≠ interpretation ≠ belief ≠ doctrine）を持ちます。**Brain**が調整し、独立した**Adversarial Audit**が挑戦します。部門横断的な調整は**MYCELIUMキャノピー層**で行われます——菌根ネットワークをモデルにした分散型・ニーズ駆動の基盤です。

> **「現在」は安価な部分です。** なぜその意思決定がなされたのか——どの証拠が支持し、どの仮定が失敗し、ガバナンスゲートが何を要求したのか——をトレースしようとした瞬間、その構造が元を取ります。

---

## 🏗️ アーキテクチャ概要

### 二層設計（論文：`MYCELIAL-GOVERNANCE-COMPLETE-THESIS.md`）

| 層 | 目的 | 主な特性 |
|------|---------|--------------|
| **Root（Rigid）** | 単一Botの内部パイプライン | 順序強制、コンテキスト分離、`EVALUATION ≠ ORIGINATION` |
| **Canopy（Emergent）** | Bot間調整 | 冗長ルーティング、相互強化、中央コントローラーなし |

```
┌─────────────────────────────────────────────────────────────┐
│  MYCELIUM Canopy Tier（涌現調整）                            │
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
│  SYNAPSIS Root Tier（各Botの剛性パイプライン）                │
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
| **先験** | SACCADE | 証拠収集前の問題フレーミング |

### 来歴層 (SENTINEL)

すべてのシグナル、エッジ変更、ゲート証拠が**非代替性・ハッシュチェーン・Ed25519署名付きプロベナンストークン**でラップされます——ガバナンスゲートの「N個の異なる経験」基準が、捏造された主張ではなく*検証済み*裏付けをカウントできるように。

---

## 🏛️ 7つの統合部門

| 部門 | 範囲 |
|------|------|
| **Finance** | Budget, CAC, ROI, FP&A, treasury |
| **Marketing** | Brand, growth, referral, paid media |
| **Sales** | Outbound, growth, Biz Dev, Corp Dev |
| **Engineering** | Product, Customer Success, Technology, Referral tech |
| **Operations** | Supply chain, procurement, day-to-day ops |
| **Legal** | Compliance, Risk, contracts, regulatory |
| **People & Comms** | HR, Internal comms, Public Affairs |

---

## 🚀 クイックスタート

```bash
# 決策システムをクローン
git clone <your-repo-url>
cd decision-systems

# 依存関係をインストール
pip install -r requirements.txt

# スペシャリストを実行
python -m kojiki.core.runner marketing-brand dispatch.json

# 全7スペシャリストを実行
python scripts/verify_all_runners.py
```

### インストール後

各エージェントは初回実行時に**Kojiki Orientation Protocol（定向プロトコル）**を実行します：

1. **Name + function** — 私は誰？
2. **Industry / sector** — リサーチをトリガー
3. **Jurisdiction**（国 / 地域 / 規制）
4. **Geography + business model**
5. **Sibling registration** — `handoffs/registry.json` の親 `group_id` 配下に登録

その後、エージェントはSYNAPSISチェーンで作業を実行し、以下で検証します：

```bash
python3 ../00-kojiki-ontology/synapsis/validate.py --mycelium-registry ../00-kojiki-ontology/handoffs/registry.json bot-output.json
```

---

## 📁 リポジトリ構造

```
decision-systems/
├── 00-kojiki-ontology/          # 共通ブレイン（コア）
│   ├── synapsis/                # SYNAPSISチェーン + バリデータ
│   │   ├── SYNAPSIS.md          # 完全仕様
│   │   ├── validate.py          # 不変条件チェッカー（標準ライブラリのみ）
│   │   ├── REFERENCES.md        # コンサルフレームワークマッピング
│   │   └── transformations.json # ステージ定義
│   ├── schemas/                 # コアJSONスキーマ（Botでミラー）
│   │   ├── evidence.json
│   │   ├── interpretation.json
│   │   ├── strategy.json
│   │   ├── problem.json
│   │   ├── learning-ledger.json
│   │   └── decision-object.json
│   ├── mycelium/                # Canopy層（涌現調整）
│   │   ├── schemas/             # node, objective, key_result, edge, signal, provenance_token
│   │   ├── engine/              # registry, graph, reinforcement, propagate, prune, sentinel, saccade
│   │   ├── neuraxis/            # 垂直軸: experience, problem, gate_request, escalation
│   │   ├── tests/               # すべて通過
│   │   └── examples/            # demo_marketing_sales.py
│   ├── learning/                # 組織記憶（ケース、パターン、ルール）
│   ├── handoffs/                # 跨部門レジストリ + ハンドオフ標準
│   ├── decision-rights/         # Own/Recommend/Consult/Approve/Execute/Escalate/Automate
│   ├── consultant/              # 50+ コンサルフレームワーク（コピー、MIT、設計時参照）
│   └── build_repos.py           # 部門リポジトリ生成
│
├── kojiki/                      # NEW: 統一ランタイム
│   ├── core/                    # 共有実行エンジン
│   │   ├── runner.py            # Slim orchestrator（約500行）
│   │   ├── stages/              # 8ステージ実行子
│   │   └── registry.py          # 専門家自動発見
│   ├── specialists/             # 専門家設定（7部門に統合）
│   │   ├── marketing-brand/
│   │   ├── marketing-growth/
│   │   ├── finance-accounting/
│   │   └── ... (7統合部門)
│   ├── configs/                 # 部門長 + 参謀長設定
│   │   ├── dept-heads/
│   │   └── chief-of-staff.yaml
│   └── cli.py                   # シンプルCLI: `kojiki decide "goal"`
│
├── scripts/                     # 検証とCI
│   ├── verify_all_runners.py
│   ├── verify_causal_signatures.py
│   └── test_runner_group.py
│
├── shared/                      # 共有リソース（シンボリックリンク）
│   ├── prompts/                 # 8ステージプロンプト
│   └── schemas/                 # 11 JSONスキーマ
│
├── test_governance_loop.py      # エンドツーエンドガバナンステスト
├── install-all.sh               # 本体 + 7部門 + メタをインストール
├── README.md
├── README.ja.md
├── README.zh.md
└── LICENSE
```

---

## 🏛️ 7つのレイヤー

| レイヤー | 答える問い | 範囲 |
|-------|---------|------|
| **KOJIKI** | 何が存在するか——本体 | エンティティ、関係、7つの統合部門 |
| **SACCADE** | 何かを試す前に問いは適切か | 先験、境界付き反復的フレーミング（収束またはパス上限） |
| **SYNAPSIS** | 1つの境界付き意思決定がどうなされるか | 単Bot、剛性、監査可能——Evidence ≠ Interpretation ≠ Strategy |
| **NEURAXIS** | 失敗が説明のためにどこまで抽象化階層を登るか | 事後、実質的乖離時のみエスカレーション、L3/L4でガバナンス |
| **MYCELIUM** | 多部門横断でどう意思決定を調整し続けるか | 創発的OKR依存グラフ、サブグラフ限定シグナル、決して指令ではない |
| **SENTINEL** | 誰が実際に言ったか | すべての部門横断主張に対する署名済み・ハッシュチェーン・非代替性プロベナンス |
| **CHIEF OF STAFF** | 誰が分解・統合するか | Goal → 分解 → 並列実行 → 統合 |

---

## ⚙️ コア概念

### SYNAPSIS変換チェーン（剛性層）

| ステージ | 権限 | 絶対になってはならないもの | 入力 | 出力スキーマ |
|-------|-----------|-----------------|-------|---------------|
| **RECORD** | 何が起きたか | — | 生入力 | `decision-object.json` |
| **SACCADE** | 本当の問いは何か？ | EVIDENCE, STRATEGY | `raw_record` | `problem.json` (P-0000) |
| **EVIDENCE** | ソースは何を確立するか？ | INTERPRETATION, STRATEGY | `raw_source`, `prior_accepted_evidence` | `evidence.json` (Verified Extracts) |
| **INTERPRETATION** | 証拠は何を意味するか？ | EVIDENCE, STRATEGY | `accepted_evidence` | `interpretation.json` |
| **STRATEGY** | 何をいつやるか？ | EVIDENCE, INTERPRETATION | `accepted_interpretation` | `strategy.json` |
| **OUTPUT** | どう実行するか？ | EVIDENCE, INTERPRETATION, STRATEGY | `accepted_strategy` | `output.json` |
| **OUTCOME** | 実際に何が起きたか？ | — | 現実 | `decision-object.json` (更新) |
| **LEARNING** | パターンを抽出 | — | Outcome vs expectation | `learning.json` |

**`kojiki/core/runner.py`が強制する不変条件：**
- `inputs_forbidden`はモデル呼び出しに*供給されない*——「しないでください」より強力
- 各ステージはスコープ付きコンテキストで別モデル呼び出し
- `validate.py`が出力をスキーマ+不変ルールでチェック

### MYCELIUM Canopy Tier（涌現）

| プリミティブ | スキーマ | キールール |
|-----------|--------|----------|
| **Node** | `node.schema.json` | `id = parent + "." + local`（血統強制） |
| **Objective** | `objective.schema.json` | 柔軟なホライズン（四半期固定ではない） |
| **Key Result** | `key_result.schema.json` | `status` + `confidence` + `depends_on[]` |
| **Edge** | `edge.schema.json` | Cross-Functional Handoffフィールド；相互性で重み強化 |
| **Signal** | `signal.schema.json` | `diagnosed_cause` + 14カテゴリ分類必須；サブグラフ限定 |

**運用サイクル**（各エッジ、各レビュー）：
```
KRステータス変更 → Signal（原因 + カテゴリ） → Subgraph（閾値 0.15）
→ Propagate（指令ではない） → Reinforce/Decay/Prune → 次のサイクル
```

**強化**（Tero et al. 2010、離散版）：
```
weight = weight * (1 - decay) + rate * (flow_signal ** gamma)
# gamma=1.15 デフォルト；lower = より冗長/耐故障
```

**剪枝**（寄生ガード）：
```
prune if weight < 0.05 OR reciprocity < 0.2
# reciprocity = reciprocal_exchanges / (reciprocal + one_directional)
```

### NEURAXIS（垂直軸）

| 層 | 範囲 | 自律性 |
|-------|-------|----------|
| **L0** Execution | 修正入力でリトライ | 自律 |
| **L1** Reasoning | 推論を修正 | 自律 |
| **L2** Problem Representation | Problemオブジェクトを置換 | 自律 |
| **L3** Ontology | オントロジー関係を修正 | **ガバナンスゲート必要** |
| **L4** Meta-Strategy | 選択メカニズムを修正 | **ガバナンスゲート必要** |

ガバナンスゲート：反復閾値（N個の異なる経験）、Decision Rights（Recommend/Consult/Approve）、失敗時クローズデフォルトのSLA。

### SENTINEL（来歴）

| プロパティ | 実装 |
|----------|----------------|
| **署名** | Ed25519、秘密鍵はノードランタイムのみ保持 |
| **非代替性** | `entry_id = hash(payload_hash + signer + prev_entry_id)` |
| **チェーン** | ログ毎（`signals.jsonl`, `edges_history.jsonl`, `gate_evidence.jsonl`） |
| **検証** | コミット前 + ガバナンスゲートが証拠を数える前 |

### Kaizen ループ（継続的改善）

| 能力 | 実装 |
|----------|----------------|
| **問題検出** | ガードレール付き結果チェック（完全性、分散、信頼度キャリブレーション） |
| **根本原因** | 14カテゴリエラー分類学によるPDCAサイクル |
| **再分類** | 失敗タイプに基づくL0→L4自動エスカレーション |
| **ガバナンス統合** | L3/L4変更はゲート承認必要 |
| **再定義取得** | 経験は置き換えProblemオブジェクトを含む |
| **学習台帳** | バージョン化されたケース、パターン、ルール——決して静かに上書きされない |

### OKR Engine (BCG Methodology)

| 能力 | 実装 |
|----------|----------------|
| **Corporate objectives** | トップレベル戦略、重み付きKRs、ホライズン柔軟性 |
| **Department objectives** | Corporateから分解、オーナー + ステータス/信頼度付きKRs |
| **Team OKRs** | 参謀長が自動生成、血統強制、depends_on[] |
| **進捗ロールアップ** | Team → Dept → Corporateの加重進捗、成熟度スコアリング |
| **ガバナンス統合** | 目的変更はL3/L4ゲート、depends_on[]でロールアウト阻止 |

### 参謀長（コーディネーター）

| 能力 | 実装 |
|----------|----------------|
| **目標分解** | パターンマッチング + LLMプランニング → 専門家タスク |
| **専門家発見** | レジストリが`specialists/<dept>/<agent>/`を自動発見 |
| **並列実行** | 独立専門家を同時に実行 |
| **依存管理** | SalesはProduct仕様を待つ；FinanceはEng見積もりを待つ |
| **競合解決** | 重複する意思決定権を検出；ガバナンスにエスカレート |
| **統合** | 統一された意思決定権を持つ単一計画にマージ |

---

## 📚 研究と参考文献

アーキテクチャは4つの独立分野の査読済み研究に基づいています：

### 生物学（菌根ネットワーク）

| 研究 | 発見 | アーキテクチャマッピング |
|-------|---------|---------------------|
| Tero et al., *Science* (2010) | Physarum強化/減衰が中央プランナーなしで効率的・耐障害トポロジーに収束 | MYCELIUM強化公式、γ効率-冗長性トレードオフ |
| Gorzelak et al., *AoB Plants* (2015) | CMN媒介植物通信の主流事例 | 信号伝播の基盤 |
| Song et al., *PLoS ONE* (2010); Babikova et al. (2013) | 防衛信号伝播（"priming"） | スコープ付きサブグラフのみSignal伝播 |
| Karst, Jones & Hoeksema, *Nature Ecology & Evolution* (2023) | 懐疑的レビュー：CMN文献の正の効果研究への引用バイアス | §II.5での警告——十分支持されたメカニズムのみ構築 |
| Frew et al., *Functional Ecology* 特集 (2025) | CMNは異質、文脈/宿主/真菌タイプ依存 | §II.5の警告を強化 |
| Silvestri et al. (2025), *New Phytologist* ステータスレポート (2026) | AM共生で新分子制御機構（`ckRNAi`）発見 | §II.6——細胞層はさらに剛性を証明し続ける |
| Bilgen & Akan, "Internet of Plants" (2024–2025, Cambridge/Koç) | 独立通信工学形式化：菌根ネットワークを"グラフベース通信媒質"として | `SIGNALING ≠ ORCHESTRATION`不変量を検証 (§IV.3, §II.7) |
| Adamatzky, *Royal Society Open Science* (2022) | 菌類電気スパイクが初歩的コードに類似する統計構造を示す | 投機的とマーク (§II.4)、負荷を支えない |

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
| 疎軌道レベル報酬→プロセスレベル信用割当 | ステップごとの信用割当が少ないデータでより良い学習を生成 | SYNAPSIS段階ごと分解、`diagnosed_cause_category`付き（学習分類学由来） |

### エンタープライズマルチAgent参照アーキテクチャ

| ソース | 発見 | アーキテクチャマッピング |
|--------|---------|---------------------|
| MicrosoftマルチAgent参照アーキテクチャ（実配備） | レジストリ→オーケストレータ→知識/状態→非同期リプレイ感知通信 | 独立して同一コンポーネント分離に到達 |

### 再帰的自己改善分類学

| 研究 | 発見 | アーキテクチャマッピング |
|-------|---------|---------------------|
| 有界 (L3) vs 無界 (L4/L5) 自己改善 | 有界：改善機構は外部維持 | `LEARNING ≠ PERMISSION TO REWRITE DOCTRINE`不変量でシステムをL3に維持 |

---

## 🔧 コンサルティングフレームワーク（設計時参照）

SYNAPSISステージは標準コンサルティングフレームワークにマッピング——ランタイム依存でなく、特定ギャップを埋める**名前付きメソッド**として：

| フレームワーク | マッピングメカニズム | セクション |
|-----------|------------------|---------|
| **5 Whys / Fishbone** | Adversarial Audit根本原因 | §III.1 |
| **MECE / Issue Tree** | EVIDENCE分解、INTERPRETATION非重複 | §III.1, III.2 |
| **Pyramid Principle / SCQ** | PRODUCTION答え優先出力 | §III.1 (OUTPUT) |
| **ケースフレームワーク** | ドメイン固有STRATEGYテンプレート | §III.1 (STRATEGY) |
| **RACI** | Decision Rightsモデル | §VII.5.5.1, §III.2 |
| **Balanced Scorecard** | Hermes KPIアーキテクチャ | §III.2 |
| **PDCA** | MYCELIUM運用サイクル | §IV.7 |
| **感度分析** | γ / decay_rate / 閾値キャリブレーション | *未定* |

完全マッピング：`synapsis/REFERENCES.md`  
フレームワークコピー元：`consultant/` (50+フレームワーク, MIT, `.git`なし)

---

## 🛣️ ロードマップ

| フェーズ | フォーカス | ステータス |
|-------|-------|--------|
| **v1** | 剛性層(SYNAPSIS) + 涌現層(MYCELIUM) + NEURAXIS + SENTINEL | ✅ 完了 |
| **v2** | Task 3決定論的採点、py_compile付きCI、合否閾値、スキーマバージョニング、拡張デモマトリックス | 📋 計画中 |
| **v3** | ステージ出力の敵対的再導出、全18部門への後付け、アーティファクト相互確認 | 📋 計画中 |

詳細は `MYCELIAL-GOVERNANCE-COMPLETE-THESIS.md` を参照。

---

## 🤝 貢献

1. **クローズドソース依存なし** — すべてMITコード
2. **ローカルファースト** — qwen2.5:14b (M1 Max 32GB) でローカル実行、クラウド不要
3. **プロバイダ非依存** — 任意のLLMを `AGENT.md` に向ける
4. **テスト必須** — PR前に `python3 -m py_compile` + バリデータ通過
5. **設計時参照のみ** — `consultant/` はコピー、依存ではない

---

## 📄 ライセンス

MIT — [LICENSE](LICENSE) を参照。

---

## 🔗 リンク

- **論文**: `MYCELIAL-GOVERNANCE-COMPLETE-THESIS.md` (二層アーキテクチャ、生物学、ガバナンス)
- **参照マッピング**: `synapsis/REFERENCES.md`
- **コンサルティングフレームワーク**: `consultant/` (50+ フレームワーク, スラッシュコマンド)
- **デモ**: `mycelium/examples/demo_marketing_sales.py`

---

**Kojiki Decision System. 決定を未監査のままにしない。**