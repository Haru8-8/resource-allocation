"""
0/1ナップサック問題 - 動的計画法（DP）

【アルゴリズム】
dp[i][w] = 最初のiアイテムから容量w以内で選べる最大価値
漸化式: dp[i][w] = max(dp[i-1][w], dp[i-1][w - weight[i]] + value[i])

【特徴】
- 時間計算量: O(n × W)
- 空間計算量: O(n × W)  ※1次元圧縮でO(W)も可能
- 厳密解（最適解を保証）
- Wが巨大な場合は非現実的（多次元問題でも同様）
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from solvers.basic.greedy_knapsack import Item, KnapsackResult, print_result, EXAMPLE_ITEMS_SMALL, EXAMPLE_CAPACITY_SMALL, EXAMPLE_ITEMS_MEDIUM, EXAMPLE_CAPACITY_MEDIUM


def dp_knapsack(items: list[Item], capacity: int) -> KnapsackResult:
    """
    DPで0/1ナップサック問題を解く（厳密解）。

    Parameters
    ----------
    items : list[Item]
        アイテムリスト
    capacity : int
        ナップサックの容量

    Returns
    -------
    KnapsackResult
        選択アイテム・総価値・総重量を含む結果

    Notes
    -----
    2次元DPテーブルを構築後、逆追跡で選択アイテムを復元する。
    容量Wが非常に大きい場合はメモリ・時間ともに非現実的になる。
    """
    n = len(items)

    # DPテーブルの初期化: dp[i][w] = 最初のiアイテムで容量w以内の最大価値
    # (n+1) × (capacity+1) の2次元配列（0行目・0列目はベースケース=0）
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    # テーブルを埋める
    for i, item in enumerate(items, start=1):
        for w in range(capacity + 1):
            # アイテムiを入れない場合
            dp[i][w] = dp[i - 1][w]
            # アイテムiを入れられる場合、入れた方が良ければ更新
            if item.weight <= w:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - item.weight] + item.value)

    # 最適値の取り出し
    best_value = dp[n][capacity]

    # 選択アイテムの逆追跡
    # dp[i][w] != dp[i-1][w] ならアイテムiを選んでいる
    selected: list[Item] = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected.append(items[i - 1])
            w -= items[i - 1].weight

    selected.reverse()  # 元の順序に戻す（任意だが見やすさのため）

    total_weight = sum(item.weight for item in selected)

    return KnapsackResult(
        selected_items=selected,
        total_value=best_value,
        total_weight=total_weight,
        capacity=capacity,
    )


def print_dp_table(items: list[Item], capacity: int) -> None:
    """
    DPテーブルを表示する（学習・デバッグ用）。
    アイテム数・容量が小さい場合のみ使用推奨。
    """
    n = len(items)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i, item in enumerate(items, start=1):
        for w in range(capacity + 1):
            dp[i][w] = dp[i - 1][w]
            if item.weight <= w:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - item.weight] + item.value)

    print("\n【DPテーブル】（行=アイテム追加後、列=容量）")
    header = "        " + "".join(f"{w:4}" for w in range(capacity + 1))
    print(header)
    print("  " + "-" * (len(header) - 2))

    row_labels = ["初期"] + [item.name[:4] for item in items]
    for i, label in enumerate(row_labels):
        row = f"  {label:<6}" + "".join(f"{dp[i][w]:4}" for w in range(capacity + 1))
        print(row)
    print()


if __name__ == "__main__":
    # ケース1: 貪欲法が最適解を逃すケース → DPで14を取れるか確認
    print("【ケース1】貪欲法が最適解を逃すケース → DPで最適解を確認")
    print_dp_table(EXAMPLE_ITEMS_SMALL, EXAMPLE_CAPACITY_SMALL)
    result_small = dp_knapsack(EXAMPLE_ITEMS_SMALL, EXAMPLE_CAPACITY_SMALL)
    print_result(result_small, "DP（ケース1）")

    # 貪欲法との比較
    from solvers.basic.greedy_knapsack import greedy_knapsack
    greedy_result = greedy_knapsack(EXAMPLE_ITEMS_SMALL, EXAMPLE_CAPACITY_SMALL)
    print(f"  貪欲法: {greedy_result.total_value} vs DP: {result_small.total_value}"
          f"  → DP が {result_small.total_value - greedy_result.total_value} 改善\n")

    # ケース2: 標準テストケース
    print("【ケース2】標準テストケース（10アイテム、容量50）")
    result_medium = dp_knapsack(EXAMPLE_ITEMS_MEDIUM, EXAMPLE_CAPACITY_MEDIUM)
    print_result(result_medium, "DP（ケース2）")

    greedy_medium = greedy_knapsack(EXAMPLE_ITEMS_MEDIUM, EXAMPLE_CAPACITY_MEDIUM)
    diff = result_medium.total_value - greedy_medium.total_value
    if diff == 0:
        print("  → 貪欲法とDP、同じ解（このケースでは貪欲法が最適解を出している）\n")
    else:
        print(f"  → DP が貪欲法より {diff} 改善\n")