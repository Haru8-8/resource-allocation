"""
拡張問題：多次元ナップサック（プロジェクト選択）
貪欲法 vs MIP vs SA の比較デモ
"""

import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from solvers.advanced.greedy_advanced import Project, greedy_advanced
from solvers.advanced.mip_knapsack import mip_knapsack
from solvers.advanced.sa_knapsack import sa_knapsack, SAConfig

st.set_page_config(page_title="拡張問題：多次元ナップサック", page_icon="🏗️", layout="wide")

st.title("🏗️ 拡張問題：多次元ナップサック")
st.caption("貪欲法・MIP（HiGHS）・SA（焼きなまし法）の比較")

st.markdown("---")

# ============================================================
# サイドバー：パラメータ設定
# ============================================================
st.sidebar.header("⚙️ パラメータ設定")

budget = st.sidebar.slider("予算上限", min_value=50, max_value=300, value=120, step=10)
manpower_limit = st.sidebar.slider("人員上限", min_value=5, max_value=50, value=20, step=1)

st.sidebar.markdown("#### 貪欲法")
alpha = st.sidebar.slider("α（予算への重み）", min_value=0.0, max_value=1.0, value=0.5, step=0.1)

st.sidebar.markdown("#### SA ハイパーパラメータ")
initial_temp = st.sidebar.slider("初期温度", min_value=10.0, max_value=500.0, value=100.0, step=10.0)
cooling_rate = st.sidebar.slider("冷却率", min_value=0.900, max_value=0.999, value=0.995, step=0.001, format="%.3f")
seed = st.sidebar.number_input("乱数シード", min_value=0, max_value=9999, value=42, step=1)

st.sidebar.markdown("#### プロジェクト設定")
st.sidebar.caption("名前・価値・予算・人員を編集できます")

default_projects = [
    {"名前": "AI開発",       "価値": 120, "予算": 50, "人員": 8},
    {"名前": "Web刷新",      "価値": 80,  "予算": 30, "人員": 5},
    {"名前": "DB移行",       "価値": 60,  "予算": 20, "人員": 4},
    {"名前": "モバイルApp",  "価値": 100, "予算": 45, "人員": 7},
    {"名前": "セキュリティ", "価値": 70,  "予算": 25, "人員": 3},
    {"名前": "分析基盤",     "価値": 90,  "予算": 40, "人員": 6},
    {"名前": "UI改善",       "価値": 40,  "予算": 15, "人員": 2},
    {"名前": "API統合",      "価値": 55,  "予算": 20, "人員": 3},
    {"名前": "クラウド移行", "価値": 110, "予算": 55, "人員": 9},
    {"名前": "自動化ツール", "価値": 65,  "予算": 25, "人員": 4},
    {"名前": "監視強化",     "価値": 45,  "予算": 18, "人員": 2},
    {"名前": "データ品質",   "価値": 50,  "予算": 22, "人員": 3},
]

edited_df = st.sidebar.data_editor(
    pd.DataFrame(default_projects),
    num_rows="dynamic",
    use_container_width=True,
)

# ============================================================
# 求解
# ============================================================
try:
    projects = [
        Project(
            name=row["名前"],
            value=int(row["価値"]),
            cost=int(row["予算"]),
            manpower=int(row["人員"]),
        )
        for _, row in edited_df.iterrows()
        if row["名前"] and int(row["予算"]) > 0 and int(row["人員"]) > 0
    ]

    if len(projects) == 0:
        st.warning("プロジェクトを1件以上入力してください")
        st.stop()

    greedy_result = greedy_advanced(projects, budget, manpower_limit, alpha=alpha)
    mip_result = mip_knapsack(projects, budget, manpower_limit)
    sa_config = SAConfig(initial_temp=initial_temp, cooling_rate=cooling_rate, seed=int(seed))
    sa_result = sa_knapsack(projects, budget, manpower_limit, config=sa_config)

except Exception as e:
    st.error(f"エラーが発生しました: {e}")
    st.stop()

# ============================================================
# 結果サマリー
# ============================================================
st.header("結果サマリー")

cols = st.columns(3)
results = [
    (greedy_result, "貪欲法"),
    (mip_result, "MIP（HiGHS）"),
    (sa_result, "SA（焼きなまし法）"),
]

for col, (result, label) in zip(cols, results):
    with col:
        st.subheader(label)
        st.metric("総価値", result.total_value)
        st.metric("予算使用", f"{result.total_cost} / {budget} ({result.budget_utilization:.1%})")
        st.metric("人員使用", f"{result.total_manpower} / {manpower_limit} ({result.manpower_utilization:.1%})")
        st.metric("求解時間", f"{result.elapsed_time:.4f} 秒")

        diff = mip_result.total_value - result.total_value
        if label == "MIP（HiGHS）":
            st.success("✅ 厳密解（最適解保証）")
        elif diff == 0:
            st.success("✅ 今回は最適解と一致")
        else:
            st.warning(f"⚠️ 最適解より **{diff}** 少ない（近似解）")

st.markdown("---")

# ============================================================
# 選択プロジェクト比較
# ============================================================
st.header("選択プロジェクト比較")

greedy_names = {p.name for p in greedy_result.selected_projects}
mip_names = {p.name for p in mip_result.selected_projects}
sa_names = {p.name for p in sa_result.selected_projects}

rows = []
for p in projects:
    rows.append({
        "プロジェクト": p.name,
        "価値": p.value,
        "予算": p.cost,
        "人員": p.manpower,
        "貪欲法": "✓" if p.name in greedy_names else "",
        "MIP": "✓" if p.name in mip_names else "",
        "SA": "✓" if p.name in sa_names else "",
    })

df_compare = pd.DataFrame(rows)
st.dataframe(df_compare, use_container_width=True, hide_index=True)

st.markdown("---")

# ============================================================
# αの影響（貪欲法）
# ============================================================
with st.expander("📊 αの影響を確認（貪欲法）"):
    st.caption("αを変えると選択プロジェクトと総価値がどう変わるか")
    alpha_rows = []
    for a in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        r = greedy_advanced(projects, budget, manpower_limit, alpha=a)
        alpha_rows.append({
            "α": a,
            "総価値": r.total_value,
            "予算使用率": f"{r.budget_utilization:.1%}",
            "人員使用率": f"{r.manpower_utilization:.1%}",
            "選択プロジェクト数": len(r.selected_projects),
            "MIPとの差": mip_result.total_value - r.total_value,
        })
    st.dataframe(pd.DataFrame(alpha_rows), use_container_width=True, hide_index=True)

st.markdown("---")

# ============================================================
# 手法解説
# ============================================================
st.header("手法解説")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("貪欲法")
    st.markdown("""
    複数制約を**重み付き正規化スコア**に集約し、
    スコア降順に選択します。

    $$\\text{score}_i = \\frac{v_i}{\\alpha \\hat{c}_i + (1-\\alpha) \\hat{m}_i}$$

    - 時間計算量：$O(n \\log n)$
    - **最適解の保証なし**
    - αの設定が恣意的で結果に影響する
    """)

with col2:
    st.subheader("MIP（HiGHS）")
    st.markdown("""
    問題を**整数計画問題**として定式化し、
    Branch & Bound で厳密解を求めます。

    $$\\max \\sum v_i x_i \\;\\text{s.t.}\\; \\sum c_i x_i \\leq B,\\; \\sum m_i x_i \\leq M$$

    - **厳密解**（最適解保証）
    - 制約追加が容易（1行追加するだけ）
    - 超大規模では求解時間が増大
    """)

with col3:
    st.subheader("SA（焼きなまし法）")
    st.markdown("""
    高温時は悪化解も受理して局所最適を脱出し、
    冷却とともに良い解に収束させます。

    $$P = \\exp\\!\\left(\\frac{\\Delta f}{T}\\right) \\quad (\\Delta f < 0)$$

    - **最適解の保証なし**（近似解）
    - 大規模問題でも実用的な時間で動作
    - 近傍操作：flip / swap / double-flip
    """)