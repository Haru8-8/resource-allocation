"""
資源配分・ナップサック問題 最適化デモ
ホーム画面：問題の概要と手法の説明
"""

import streamlit as st

st.set_page_config(
    page_title="ナップサック最適化デモ",
    page_icon="🎒",
    layout="wide",
)

st.title("🎒 ナップサック問題 最適化デモ")
st.caption("資源配分問題を複数の手法で解き、結果を比較します")

st.markdown("---")

st.header("問題の概要")
st.markdown("""
**ナップサック問題**とは、容量制限のある「ナップサック」にアイテムを詰める際、
**総価値を最大化**する組み合わせを求める問題です。

工場への設備配置・プロジェクト予算配分・投資ポートフォリオ最適化など、
現実の資源配分問題の基礎モデルとして広く使われています。
""")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📦 基本問題：0/1ナップサック")
    st.markdown("""
    **制約**：重量1つ

    $$\\max \\sum v_i x_i \\quad \\text{s.t.} \\quad \\sum w_i x_i \\leq W,\\; x_i \\in \\{0,1\\}$$

    | 手法 | 特徴 |
    |------|------|
    | 貪欲法 | 価値密度順に選択。高速だが最適解の保証なし |
    | DP | 動的計画法による厳密解。制約数が増えると破綻 |
    """)

with col2:
    st.subheader("🏗️ 拡張問題：多次元ナップサック")
    st.markdown("""
    **制約**：予算・人員の2つ

    $$\\max \\sum v_i x_i \\quad \\text{s.t.} \\quad \\sum c_i x_i \\leq B,\\; \\sum m_i x_i \\leq M,\\; x_i \\in \\{0,1\\}$$

    | 手法 | 特徴 |
    |------|------|
    | 貪欲法 | 重み付きスコア順に選択。αの設定が結果に影響 |
    | MIP | PuLP/HiGHSによる厳密解。実務標準 |
    | SA | 焼きなまし法による近似解。大規模問題向け |
    """)

st.markdown("---")
st.info("👈 左のサイドバーから **基本問題** または **拡張問題** を選択してください")