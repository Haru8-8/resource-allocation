"""
基本問題：0/1ナップサック
貪欲法 vs DP の比較デモ
"""

import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from solvers.basic.greedy_knapsack import Item, greedy_knapsack
from solvers.basic.dp_knapsack import dp_knapsack

st.set_page_config(page_title="基本問題：0/1ナップサック", page_icon="📦", layout="wide")

st.title("📦 基本問題：0/1ナップサック")
st.caption("貪欲法（価値密度順）と動的計画法（DP）の比較")

st.markdown("---")

# ============================================================
# サイドバー：パラメータ設定
# ============================================================
st.sidebar.header("⚙️ パラメータ設定")

capacity = st.sidebar.slider("ナップサックの容量 W", min_value=10, max_value=200, value=50, step=5)

st.sidebar.markdown("#### アイテム設定")
st.sidebar.caption("名前・価値・重量を編集できます")

default_items = [
    {"名前": "laptop",    "価値": 150, "重量": 30},
    {"名前": "camera",    "価値": 35,  "重量": 5},
    {"名前": "tablet",    "価値": 80,  "重量": 15},
    {"名前": "headphone", "価値": 40,  "重量": 8},
    {"名前": "book_set",  "価値": 60,  "重量": 20},
    {"名前": "clothes",   "価値": 25,  "重量": 10},
    {"名前": "charger",   "価値": 20,  "重量": 4},
    {"名前": "shoes",     "価値": 30,  "重量": 12},
    {"名前": "snacks",    "価値": 10,  "重量": 5},
    {"名前": "umbrella",  "価値": 15,  "重量": 6},
]

edited_df = st.sidebar.data_editor(
    pd.DataFrame(default_items),
    num_rows="dynamic",
    use_container_width=True,
)

# ============================================================
# 求解
# ============================================================
try:
    items = [
        Item(name=row["名前"], value=int(row["価値"]), weight=int(row["重量"]))
        for _, row in edited_df.iterrows()
        if row["名前"] and int(row["重量"]) > 0
    ]

    if len(items) == 0:
        st.warning("アイテムを1件以上入力してください")
        st.stop()

    greedy_result = greedy_knapsack(items, capacity)
    dp_result = dp_knapsack(items, capacity)

except Exception as e:
    st.error(f"エラーが発生しました: {e}")
    st.stop()

# ============================================================
# 結果サマリー
# ============================================================
st.header("結果サマリー")

col1, col2 = st.columns(2)

def render_summary(col, result, label, is_optimal: bool):
    with col:
        st.subheader(label)
        m1, m2, m3 = st.columns(3)
        m1.metric("総価値", result.total_value)
        m2.metric("総重量", f"{result.total_weight} / {capacity}")
        m3.metric("容量使用率", f"{result.utilization:.1%}")
        if is_optimal:
            st.success("✅ 厳密解（最適解保証）")
        else:
            diff = dp_result.total_value - result.total_value
            if diff == 0:
                st.success("✅ 今回は最適解と一致")
            else:
                st.warning(f"⚠️ 最適解より **{diff}** 少ない（近似解）")

render_summary(col1, greedy_result, "貪欲法", is_optimal=False)
render_summary(col2, dp_result, "DP（動的計画法）", is_optimal=True)

st.markdown("---")

# ============================================================
# 選択アイテム比較
# ============================================================
st.header("選択アイテム比較")

greedy_names = {item.name for item in greedy_result.selected_items}
dp_names = {item.name for item in dp_result.selected_items}

rows = []
for item in items:
    in_greedy = "✓" if item.name in greedy_names else ""
    in_dp = "✓" if item.name in dp_names else ""
    rows.append({
        "アイテム": item.name,
        "価値": item.value,
        "重量": item.weight,
        "密度": round(item.density, 3),
        "貪欲法": in_greedy,
        "DP": in_dp,
    })

df_compare = pd.DataFrame(rows).sort_values("密度", ascending=False).reset_index(drop=True)
st.dataframe(df_compare, use_container_width=True, hide_index=True)

st.markdown("---")

# ============================================================
# DPテーブル（折りたたみ）
# ============================================================
with st.expander("📊 DPテーブルを表示（アイテム数・容量が小さい場合推奨）"):
    if len(items) > 15 or capacity > 100:
        st.warning("アイテム数が多いか容量が大きいため表示が見づらくなる場合があります")

    n = len(items)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i, item in enumerate(items, start=1):
        for w in range(capacity + 1):
            dp[i][w] = dp[i - 1][w]
            if item.weight <= w:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - item.weight] + item.value)

    row_labels = ["初期"] + [item.name for item in items]
    df_dp = pd.DataFrame(dp, index=row_labels, columns=list(range(capacity + 1)))
    st.dataframe(df_dp, use_container_width=True)

# ============================================================
# 手法解説
# ============================================================
st.markdown("---")
st.header("手法解説")

col1, col2 = st.columns(2)

with col1:
    st.subheader("貪欲法")
    st.markdown("""
    **価値密度**（価値 ÷ 重量）の降順にアイテムをソートし、
    容量に収まるものから順に選択します。

    - 時間計算量：$O(n \\log n)$
    - **最適解の保証なし**
    - 密度が高くても「残り容量の使い方」を考慮しないため取りこぼしが起きる
    """)

with col2:
    st.subheader("DP（動的計画法）")
    st.markdown("""
    $dp[i][w]$「最初の $i$ 個から容量 $w$ 以内で選べる最大価値」を
    漸化式で埋めていきます。

    $$dp[i][w] = \\max(dp[i-1][w],\\; dp[i-1][w-w_i] + v_i)$$

    - 時間計算量：$O(n \\times W)$
    - **厳密解**（最適解保証）
    - 制約が増えるとテーブルが多次元化し現実的でなくなる → MIPへ
    """)