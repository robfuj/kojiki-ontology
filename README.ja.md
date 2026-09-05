# Kojiki Decision System / Kojiki 意思決定システム / Kojiki 决策系统

**あらゆるLLMを意思決定中心の組織に変える、ローカルファーストでオープンソースのフレームワーク。**

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![Tests Passing](https://img.shields.io/badge/Tests-All%20Passing-brightgreen.svg)](#testing)
[![OpenViking Compatible](https://img.shields.io/badge/OpenViking-Compatible-orange.svg)](https://github.com/volcengine/OpenViking)

---

## 🌐 Language / 言語 / 语言

[**English**](README.md) • [**日本語**](README.ja.md) • [**中文**](README.zh.md)

---

## 🎯 これは何か？

Kojikiは、あらゆるLLM（Claude、GPT、ローカルモデル、エージェントハーネス）に**共有可能で監査可能な意思決定構造**を与えます——単なるチャットではありません。すべての部門エージェントが同じ**SYNAPSIS変換チェーン**を通じて推論します：

```
RECORD → SACCADE → EVIDENCE → INTERPRETATION → STRATEGY → OUTPUT → OUTCOME → LEARNING
```

各ステージは**境界付き変換**であり、明示的な権限と「決してサイレントに変化してはならないもの」（evidence ≠ interpretation ≠ belief ≠ doctrine）を持ちます。**Brain**がオーケストレーションし、独立した**Adversarial Audit（敵対的監査）**が挑戦します。部門横断の調整は**MYCELIUMキャノピー層**を通じて行われます——菌根ネットワークをモデルにした、分散型・需要駆動の基盤です。

> **「現在は安い部分だ。」** なぜその意思決定がなされたのか——何の証拠がそれを支え、何の仮定が失敗し、ガバナンスゲートが何を要求したのか——を遡ろうとした瞬間、構造がその価値を証明します。

---

## 🏗️ アーキテクチャ概要

### 二層設計（論文：`MYCELIAL-GOVERNANCE-COMPLETE-THESIS.md`）

| 層 | 目的 | 主要特性 |
|------|------|----------|
| **Root（剛性）** | 単一ボットの内部パイプライン | 強制順序、コンテキスト分離、`EVALUATION ≠ ORIGINATION` |
| **Canopy（創発）** | ボット間調整 | 冗長ルーティング、相互強化、中央コントローラなし |

```
┌─────────────────────────────────────────────────────────────┐
│  MYCELIUM Canopy Tier（創発的調整）                          │
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
│  SYNAPSIS Root Tier（ボット単位の剛性パイプライン）           │
│  RECORD → SACCADE → EVIDENCE → INTERPRETATION → STRATEGY    │
│       → OUTPUT → OUTCOME → LEARNING                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │Runner.py│  │Schema   │  │Adversary│  │Brain    │        │
│  │context  │  │validate │  │Audit    │  │adjudicate│        │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### 3つの垂直軸

| 軸 | コンポーネント | 目的 |
|------|---------------|------|
| **水平** | MYCELIUM | 部門横断調整（OKR基盤） |
| **垂直** | NEURAXIS | 再帰的問題再定義（L0–L4エスカレーション） |
| **事前** | SACCADE | 証拠収集前の問題フレーミング |

### 由来層（SENTINEL）

すべてのシグナル、エッジ変更、ゲート証拠は**非代替性・ハッシュチェーン・Ed25519署名付きの由来トークン**でラップされます——ガバナンスゲートの「N個の異なる経験」基準が、捏造された主張ではなく**検証済みの裏付け**を数えるためです。

---

## 🏛️ 7つの層

| 層 | 答える問い | スコープ |
|------|-----------|----------|
| **KOJIKI** | 何が存在するか — オントロジー | エンティティ、関係、20の標準部門 |
| **SACCADE** | 試す前に問いが適切か | 事前、反復的フレーミング（収束またはパス上限） |
| **SYNAPSIS** | 1つの境界付き決定がどう作られるか | ボット単位、剛性、監査可能 — Evidence ≠ Interpretation ≠ Strategy |
| **NEURAXIS** | 失敗を説明するために抽象梯子をどこまで登るか | 事後、実発散時のみエスカレート、L3/L4でガバナンス |
| **MYCELIUM** | 多数部門の多数決定がどう協調するか | 創発的OKR依存グラフ、サブグラフスコープSignal、指示ではない |
| **SENTINEL** | 実際に誰が言ったか | すべてのクロスノード主張に署名・ハッシュチェーン・非代替性の由来 |

---

## 🚀 クイックスタート

```bash
# 決定システムをクローン
git clone https://github.com/robfuj/Narro  # またはあなたのフォーク
cd decision-systems

# フルパッケージをインストール：オントロジー + 20部門 + 2メタエージェント
bash install-all.sh

# または単一の部門をインストール（オントロジー兄弟を自動クローン）
cd 03-marketing
bash bots/install_bots.py brand growth
```

### インストール後

各エージェントは初回実行時に**Kojiki Orientation Protocol（オリエンテーションプロトコル）**を実行します：
1. **Name + function** — 私は誰か？
2. **Industry / sector** — リサーチをトリガー
3. **Jurisdiction**（国 / 地域 / 規制）
4. **Geography + business model**
5. **Sibling registration** — 親`group_id`の下で`handoffs/registry.json`に登録

その後、エージェントはSYNAPSISチェーンを通じて作業を実行し、以下で検証します：
```bash
python3 ../00-kojiki-ontology/synapsis/validate.py --mycelium-registry ../00-kojiki-ontology/handoffs/registry.json bot-output.json
```

---

## 📁 リポジトリ構造

```
decision-systems/
├── 00-kojiki-ontology/          # 共有ブレイン（ここがコア）
│   ├── synapsis/                # SYNAPSISチェーン + バリデータ
│   │   ├── SYNAPSIS.md          # 完全仕様
│   │   ├── validate.py          # 不変条件チェッカー（stdlibのみ）
│   │   ├── REFERENCES.md        # コンサルティングフレームワーク対応表
│   │   └── transformations.json # ステージ定義
│   ├── schemas/                 # コアJSONスキーマ（ボットにミラーリング）
│   │   ├── evidence.json
│   │   ├── interpretation.json
│   │   ├── strategy.json
│   │   ├── problem.json
│   │   ├── learning-ledger.json
│   │   └── decision-object.json
│   ├── mycelium/                # Canopy層（創発的調整）
│   │   ├── schemas/             # node, objective, key_result, edge, signal, provenance_token
│   │   ├── engine/              # registry, graph, reinforcement, propagate, prune, sentinel, saccade
│   │   ├── neuraxis/            # 垂直軸: experience, problem, gate_request, escalation
│   │   ├── tests/               # すべて通過
│   │   └── examples/            # demo_marketing_sales.py
│   ├── learning/                # 組織記憶（ケース、パターン、ルール）
│   ├── handoffs/                # 部門横断レジストリ + ハンドオフ標準
│   ├── decision-rights/         # Own/Recommend/Consult/Approve/Execute/Escalate/Automate
│   ├── consultant/              # yoichiojima-2/consultant（コピー、MIT、設計時参照）
│   └── build_repos.py           # 20部門リポを生成
│
├── 01-executive-strategy/       # 部門リポ（各独立）
├── 02-finance/
├── 03-marketing/
├── 04-sales/
├── ... (計20)
│
├── 21-executive-org-builder/    # メタ：どの幹部エージェントをインストールするか尋ねる
└── 22-decision-system-installer/# メタ：スタック全体をインストール
```

各部門リポの内容：
```
03-marketing/
├── bots/
│   ├── install_bots.py          # オンデマンド サブ機能インストーラ
│   ├── manifest.json            # サブ機能 + transformation_pipeline
│   └── <slug>/                  # サブ機能ごとに1つ（例: brand, growth）
│       ├── AGENT.md             # エントリーポイント + オリエンテーションプロトコル
│       ├── runner.py            # コンテキスト分離パイプライン実行器
│       ├── pipeline/            # 5ステージプロンプト
│       │   ├── 01-saccade.md
│       │   ├── 02-evidence.md
│       │   ├── 03-interpretation.md
│       │   ├── 04-strategy.md
│       │   └── 05-output.md
│       ├── schema/              # 00-kojiki-ontologyスキーマのミラー
│       ├── data/                # example.json（スタブ決定オブジェクト）
│       └── tools/validate.py    # 拡張バリデータ
└── README.md
```

---

## ⚙️ コア概念

### SYNAPSIS変換チェーン（剛性層）

| ステージ | 権限 | なってはならないもの | 入力 | 出力スキーマ |
|----------|------|---------------------|------|--------------|
| **RECORD** | 何が起きたか | — | 生入力 | `decision-object.json` |
| **SACCADE** | 本当の問いは何か？ | EVIDENCE, STRATEGY | `raw_record` | `problem.json` (P-0000) |
| **EVIDENCE** | ソースが何を確立するか？ | INTERPRETATION, STRATEGY | `raw_source`, `prior_accepted_evidence` | `evidence.json` (Verified Extracts) |
| **INTERPRETATION** | 証拠は何を意味するか？ | EVIDENCE, STRATEGY | `accepted_evidence` | `interpretation.json` |
| **STRATEGY** | 何をすべきか、いつか？ | EVIDENCE, INTERPRETATION | `accepted_interpretation` | `strategy.json` |
| **OUTPUT** | どう実行するか？ | EVIDENCE, INTERPRETATION, STRATEGY | `accepted_strategy` | `output.json` |
| **OUTCOME** | 実際に何が起きたか？ | — | 現実 | `decision-object.json` (更新) |
| **LEARNING** | パターンを抽出 | — | 結果 vs 期待 | `learning-ledger.json` |

**`runner.py`によって強制される不変条件**（負荷を支えるコンポーネント）：
- `inputs_forbidden`はモデル呼び出しに**供給されない**——「しないでください」より強力
- 各ステージ = スコープされたコンテキストでの別モデル呼び出し
- `validate.py`が出力をスキーマ + 不変条件ルールでチェック

### MYCELIUM Canopy層（創発）

| プリミティブ | スキーマ | キールール |
|-------------|----------|------------|
| **Node** | `node.schema.json` | `id = parent + "." + local`（系譜強制） |
| **Objective** | `objective.schema.json` | 柔軟なホライズン（四半期固定ではない） |
| **Key Result** | `key_result.schema.json` | `status` + `confidence` + `depends_on[]` |
| **Edge** | `edge.schema.json` | Cross-Functional Handoffフィールド；相互性で重み強化 |
| **Signal** | `signal.schema.json` | `diagnosed_cause` + 14カテゴリ分類必須；サブグラフ境界 |

**運用サイクル**（エッジごと、レビューごと）：
```
KRステータス変更 → Signal（原因 + カテゴリ） → Subgraph（閾値0.15）
→ Propagate（指示ではない） → Reinforce/Decay/Prune → 次サイクル
```

**強化**（Tero et al. 2010、離散版）：
```
weight = weight * (1 - decay) + rate * (flow_signal ** gamma)
# gamma=1.15デフォルト；低い = より冗長/耐障害
```

**剪定**（寄生防止ガード）：
```
prune if weight < 0.05 OR reciprocity < 0.2
# reciprocity = reciprocal_exchanges / (reciprocal + one_directional)
```

### NEURAXIS（垂直軸）

| 層 | スコープ | 自律性 |
|------|----------|--------|
| **L0** Execution | 修正入力で再試行 | 自律 |
| **L1** Reasoning | 推論の修正 | 自律 |
| **L2** Problem Representation | Problemオブジェクトの置換 | 自律 |
| **L3** Ontology | オントロジー関係の修正 | **ガバナンスゲート必須** |
| **L4** Meta-Strategy | 選択機構の修正 | **ガバナンスゲート必須** |

ガバナンスゲート（§VII.5.5.1）：反復閾値（N個の異なる経験）、意思決定権利、SLAとフェイルクローズドデフォルト。

### SENTINEL（由来証明）

| 特性 | 実装 |
|----------|--------------|
| **署名** | Ed25519、秘密鍵はノードランタイムのみが保持 |
| **非代替性** | `entry_id = hash(payload_hash + signer + prev_entry_id)` |
| **チェーン** | ログごと（`signals.jsonl`, `edges_history.jsonl`, `gate_evidence.jsonl`） |
| **検証** | コミット前 + ガバナンスゲートの証拠カウント前 |

---

## 🧪 テスト

```bash
cd 00-kojiki-ontology/mycelium
PYTHONPATH=../ python3 tests/test_registry.py
PYTHONPATH=../ python3 tests/test_graph.py
PYTHONPATH=../ python3 tests/test_reinforcement.py
PYTHONPATH=../ python3 tests/test_propagate.py
PYTHONPATH=../ python3 tests/test_prune.py
PYTHONPATH=../ python3 tests/test_sentinel.py
# すべてのテストが通過
```

動作例の実行：
```bash
PYTHONPATH=../ python3 examples/demo_marketing_sales.py
```

---

## 📚 研究・参考文献

アーキテクチャは4つの独立した分野における査読済み研究に基づいています：

### 生物学（菌根ネットワーク）
| 研究 | 発見 | アーキテクチャへの対応 |
|------|------|---------------------|
| Tero et al., *Science* (2010) | Physarumの強化/減衰が中央計画者なしで効率的・耐障害なトポロジに収束 | MYCELIUM強化式（§IV.6.1）、γ効率-冗長性トレードオフ |
| Gorzelak et al., *AoB Plants* (2015) | CMNを介した植物通信の主流事例 | シグナル伝播の基盤（§II.2, §IV.6.3） |
| Song et al., *PLoS ONE* (2010); Babikova et al. (2013) | 防御シグナル伝播（"priming"） | スコープ付きサブグラフのみのSignal伝播 |
| Karst, Jones & Hoeksema, *Nature Ecology & Evolution* (2023) | 懐疑的レビュー：CMN文献における正の効果研究への引用バイアス | §II.5の注意喚起——十分支持されたメカニクスのみ採用 |
| Frew et al., *Functional Ecology* special issue (2025) | CMNは異質、文脈/ホスト/菌類タイプ依存 | §II.5の注意を補強 |
| Silvestri et al. (2025), *New Phytologist* status report (2026) | AM共生における新分子制御機構（`ckRNAi`）発見 | §II.6——細胞層はますます剛性が高いことが判明 |
| Bilgen & Akan, "Internet of Plants" (2024–2025, Cambridge/Koç) | 独立した通信工学形式化：菌類ネットワークを「グラフベース通信媒質」として定義 | `SIGNALING ≠ ORCHESTRATION`不変条件を検証（§IV.3, §II.7） |
| Adamatzky, *Royal Society Open Science* (2022) | 菌類の電気的スパイクが初歩的コードに類似した統計構造を示す | 投機的として明記（§II.4）、負荷には使わない |

### 神経科学（階層的予測符号化）
| 研究 | 発見 | アーキテクチャへの対応 |
|------|------|---------------------|
| Rao & Ballard (1999) | 階層的予測符号化：予測は下方、残差誤差は上方；誤差は吸収されるまで上昇 | NEURAXISエスカレーションラダー（§VII.5.2）——完全同一の計算構造 |
| 脊髄 → 延髄 → 大脳皮質の反射弧 | 高速局所反応；曖昧刺激はエスカレート；皮質抑制が反射を変調 | NEURAXIS L0–L4層、L3でガバナンスゲート |

### 免疫学（自然/獲得免疫境界）
| 研究 | 発見 | アーキテクチャへの対応 |
|------|------|---------------------|
| 自然免疫（TLR、固定） → 獲得免疫（抗体、記憶） | 獲得免疫は自然免疫に学習層を補完；自然免疫認識機構を書き換えない | NEURAXISガバナンスゲート：L0–L2自律、L3–L4は外部検証必須（§VII.5.2, §VII.5.5） |

### LLMへの強化学習研究
| 研究 | 発見 | アーキテクチャへの対応 |
|------|------|---------------------|
| 稀な軌道レベル報酬 → プロセスレベル信用割当 | ステップ単位の信用割当は少ないデータでより良い学習 | SYNAPSIS段階別分解、`diagnosed_cause_category`はLearning Taxonomyから |

### エンタープライズマルチエージェント参照アーキテクチャ
| ソース | 発見 | アーキテクチャへの対応 |
|--------|------|---------------------|
| Microsoftマルチエージェント参照アーキテクチャ（実導入ベース） | レジストリ → オーケストレータ → 知識/状態 → 非同期リプレイ対応通信 | 同じコンポーネント分離に独立して到達 |

### 再帰的自己改善タクソノミー
| 研究 | 発見 | アーキテクチャへの対応 |
|------|------|---------------------|
| 有界（L3）vs 無界（L4/L5）自己改善 | 有界：改善機構は外部維持 | `LEARNING ≠ PERMISSION TO REWRITE DOCTRINE`不変条件でシステムをL3に維持 |

---

## 🔧 コンサルティングフレームワーク（設計時参照）

SYNAPSISステージは標準的なコンサルティングフレームワークに対応します——ランタイム依存ではなく、特定のギャップを埋めるための**名前付きメソッド**として：

| フレームワーク | 対応メカニズム | セクション |
|--------------|---------------|----------|
| **5 Whys / Fishbone** | Adversarial Audit根本原因 | §III.1 |
| **MECE / Issue Tree** | EVIDENCE分解、INTERPRETATION非重複 | §III.1, III.2 |
| **Pyramid Principle / SCQ** | PRODUCTION答え優先出力 | §III.1 (OUTPUT) |
| **ケースフレームワーク** | ドメイン固有STRATEGYテンプレート | §III.1 (STRATEGY) |
| **RACI** | 意思決定権利モデル | §VII.5.5.1, §III.2 |
| **Balanced Scorecard** | Hermes KPIアーキテクチャ | §III.2 |
| **PDCA** | MYCELIUM運用サイクル | §IV.7 |
| **Sensitivity Analysis** | γ / decay_rate / 閾値校正 | *未解決項目* |

完全対応表：`synapsis/REFERENCES.md`  
フレームワークコピー元：`consultant/` (yoichiojima-2/consultant, MIT, `.git`なし)

---

## 🛣️ ロードマップ

| フェーズ | フォーカス | ステータス |
|----------|-----------|----------|
| **v1** | 剛性層（SYNAPSIS）+ 創発層（MYCELIUM）+ NEURAXIS + SENTINEL | ✅ 完了 |
| **v2** | Task 3決定論的採点、CI py_compile、合否閾値、スキーマバージョニング、デモマトリクス拡張 | 📋 計画中 |
| **v3** | ステージ出力の敵対的再導出、全20部門への後付け、アーティファクト相互検証 | 📋 計画中 |

詳細は`MYCELIAL-GOVERNANCE-COMPLETE-THESIS.md`を参照。

---

## 🤝 貢献

1. **クローズドソース依存なし** — すべてのコードMIT、外部参照はAGPL-3.0（OpenViking）のみ
2. **ローカルファースト** — qwen2.5:14b（M1 Max 32GB）で動作、クラウド不要
3. **プロバイダ非依存** — 任意のLLMを`AGENT.md`に向ける
4. **テスト必須** — `python3 -m py_compile` + バリデータ通過をPR前に実行
3. **設計時参照のみ** — `consultant/`はコピーであり依存ではない

---

## 📄 ライセンス

MIT — [LICENSE](LICENSE)を参照。

OpenViking（オプションメモリバックエンド）はAGPL-3.0、外部、バンドルなし。

---

## 🔗 リンク

- **論文**: `MYCELIAL-GOVERNANCE-COMPLETE-THESIS.md`（二層アーキテクチャ、生物学、ガバナンス）
- **参照対応表**: `synapsis/REFERENCES.md`
- **コンサルティングフレームワーク**: `consultant/`（50+フレームワーク、スラッシュコマンド）
- **デモ**: `mycelium/examples/demo_marketing_sales.py`

---

**Kojiki Decision System. 決定を監査なしに残さない。**