# 資源配分・ナップサック最適化（Resource Allocation Optimizer）

0/1ナップサック問題・多次元ナップサック問題（プロジェクト選択）を、貪欲法・DP・MIP・SAの複数手法で比較実装したポートフォリオです。

👉 **同一問題インスタンスに対して複数手法を実行し、解の品質・求解時間を定量的に比較できます。**

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.56+-red?logo=streamlit)
![PuLP](https://img.shields.io/badge/Optimization-PuLP-yellow)
![License: MIT](https://img.shields.io/badge/License-MIT-green)

---

## 解決できる課題

- 複数の制約（予算・人員など）のもとで最大価値の組み合わせを選びたい
- 貪欲法・厳密解法・メタヒューリスティクスの性能差を実際に比較したい
- 最適性保証のある手法と高速な近似手法の使い分けを理解したい

---

## 想定ユースケース

- 予算・人員制約のもとでのプロジェクト選択
- 投資ポートフォリオの最適化
- 資材・設備の配置・調達計画

---

## デモ

### デモURL
Streamlit Cloud でインタラクティブデモを公開しています。  
→ **公開後にURLを記載予定**

---

## 問題設定

### 基本問題：0/1ナップサック（1制約）

容量制限のあるナップサックにアイテムを詰め、総価値を最大化する。

$$\max \sum_{i} v_i x_i \quad \text{s.t.} \quad \sum_{i} w_i x_i \leq W, \quad x_i \in \{0, 1\}$$

### 拡張問題：多次元ナップサック（2制約）

予算・人員の2制約のもとでプロジェクトを選択し、総価値（期待利益）を最大化する。

$$\max \sum_{i} v_i x_i \quad \text{s.t.} \quad \sum_{i} c_i x_i \leq B, \quad \sum_{i} m_i x_i \leq M, \quad x_i \in \{0, 1\}$$

---

## 実装アルゴリズム

### 基本問題

| 手法 | 概要 | 最適性 | 計算量 |
|------|------|--------|--------|
| 貪欲法 | 価値密度（価値/重量）順に選択 | 近似解 | O(n log n) |
| DP | 動的計画法による全探索 | 厳密解 | O(n × W) |

### 拡張問題

| 手法 | 概要 | 最適性 | 計算量 |
|------|------|--------|--------|
| 貪欲法 | 重み付き正規化スコア順に選択 | 近似解 | O(n log n) |
| MIP | PuLP/HiGHSによる整数計画 | 厳密解 | - |
| SA | 焼きなまし法による近似探索 | 近似解 | - |

---

## アルゴリズムの使い分け

| 観点 | 貪欲法 | DP | MIP | SA |
|------|--------|-----|-----|-----|
| 最適性保証 | なし | あり | あり | なし |
| 多次元制約 | 対応（スコア集約） | 次元の呪いで破綻 | 対応（1行追加） | 対応 |
| 大規模問題 | 高速 | W依存で破綻 | 計算時間増大 | 比較的安定 |
| 実装の透明性 | 高い | 高い | ソルバー任せ | ロジックが見える |

---

## 関連記事

- （執筆予定）Pythonによる0/1ナップサック問題の貪欲法・DP実装と比較
- （執筆予定）Pythonによる多次元ナップサック問題の貪欲法・MIP・SA実装と比較

---

## 主な機能

- **パラメータの柔軟な設定**: 容量・予算・人員上限、アイテム・プロジェクト一覧をUIで変更可能
- **基本問題・拡張問題の個別デモ**: 各ページで手法ごとの結果確認が可能
- **選択アイテムの比較表**: 各手法がどのアイテム/プロジェクトを選んだかを横並びで比較
- **DPテーブルの可視化**: 動的計画法の状態遷移テーブルをインタラクティブに確認
- **αの影響分析**: 貪欲法のスコア重みパラメータαを変化させたときの結果変化を一覧表示
- **SAハイパーパラメータ調整**: 初期温度・冷却率・乱数シードをUIで変更可能

---

## ファイル構成

```
resource-allocation/
├── app.py                       # ホーム画面（問題概要・手法説明）
├── requirements.txt
├── pages/
│   ├── 1_basic.py               # 基本問題デモ（貪欲法 vs DP）
│   └── 2_advanced.py            # 拡張問題デモ（貪欲法 vs MIP vs SA）
└── solvers/
    ├── basic/
    │   ├── greedy_knapsack.py   # 貪欲法（0/1ナップサック）
    │   └── dp_knapsack.py       # DP（0/1ナップサック）
    └── advanced/
        ├── greedy_advanced.py   # 貪欲法（多次元ナップサック）
        ├── mip_knapsack.py      # MIP（PuLP/HiGHS）
        └── sa_knapsack.py       # SA（焼きなまし法）
```

---

## ローカルで実行

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# アプリの起動
streamlit run app.py
```

### 各ソルバーの単体実行

```bash
# 基本問題
python solvers/basic/greedy_knapsack.py
python solvers/basic/dp_knapsack.py

# 拡張問題
python solvers/advanced/greedy_advanced.py
python solvers/advanced/mip_knapsack.py
python solvers/advanced/sa_knapsack.py
```

---

## 技術スタック

| 分類 | 技術 |
|------|------|
| 最適化（MIP） | PuLP + HiGHS |
| 最適化（DP・貪欲法・SA） | スクラッチ実装 |
| フレームワーク | Streamlit |
| データ処理 | pandas |

---

## 技術的なポイント

- **貪欲法のスコア設計**: 複数制約を重み付き正規化スコアに集約。αパラメータの恣意性をUIで可視化し、MIPの優位性を対比
- **SAの近傍設計**: flip / swap / double-flipの3種の近傍操作を使用。swapにより「同じ制約消費量で価値を上げる」移動を実現
- **ペナルティ法による制約処理**: SA内で制約違反解にペナルティを与え、実行可能解への誘導と局所最適脱出を両立

---

## 備考

最適化アルゴリズムの実装・比較を目的として開発したプロジェクトです。「基本問題では厳密解（DP）、多次元化後は整数計画（MIP）とメタヒューリスティクス（SA）」という手法選択の流れを、実装と定量比較で示しています。

---

## ライセンス

[MIT License](LICENSE)