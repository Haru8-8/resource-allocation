"""
0/1ナップサック問題 - 貪欲法（価値密度順）

【アルゴリズム】
アイテムを価値/重量（価値密度）の降順にソートし、
容量に収まるものから順番に選択していく近似解法。

【特徴】
- 時間計算量: O(n log n) ← ソートが支配的
- 最適解の保証なし（近似解）
- 実装が単純でスケールしやすい
"""

from dataclasses import dataclass


@dataclass
class Item:
    """ナップサック問題の1アイテム"""
    name: str
    value: int
    weight: int

    @property
    def density(self) -> float:
        """価値密度（単位重量あたりの価値）"""
        return self.value / self.weight


@dataclass
class KnapsackResult:
    """解の格納用データクラス"""
    selected_items: list[Item]
    total_value: int
    total_weight: int
    capacity: int

    @property
    def utilization(self) -> float:
        """容量使用率"""
        return self.total_weight / self.capacity


def greedy_knapsack(items: list[Item], capacity: int) -> KnapsackResult:
    """
    貪欲法で0/1ナップサック問題を解く。

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
    価値密度の降順でソートし、容量に収まるアイテムを貪欲に選択する。
    最適解を保証しないが、O(n log n) で動作する高速な近似解法。
    """
    # 価値密度の降順にソート
    # 同密度の場合は価値の大きい方を優先（タイブレーク）
    sorted_items = sorted(items, key=lambda x: (x.density, x.value), reverse=True)

    selected: list[Item] = []
    remaining_capacity = capacity

    for item in sorted_items:
        if item.weight <= remaining_capacity:
            selected.append(item)
            remaining_capacity -= item.weight

    total_value = sum(item.value for item in selected)
    total_weight = sum(item.weight for item in selected)

    return KnapsackResult(
        selected_items=selected,
        total_value=total_value,
        total_weight=total_weight,
        capacity=capacity,
    )


def print_result(result: KnapsackResult, algorithm_name: str = "貪欲法") -> None:
    """結果を整形して表示する"""
    print(f"\n{'='*45}")
    print(f"  {algorithm_name} - 結果")
    print(f"{'='*45}")
    print(f"  総価値    : {result.total_value}")
    print(f"  総重量    : {result.total_weight} / {result.capacity}")
    print(f"  容量使用率: {result.utilization:.1%}")
    print(f"\n  選択アイテム ({len(result.selected_items)}個):")
    print(f"  {'名前':<12} {'価値':>6} {'重量':>6} {'密度':>8}")
    print(f"  {'-'*36}")
    for item in result.selected_items:
        print(f"  {item.name:<12} {item.value:>6} {item.weight:>6} {item.density:>8.3f}")
    print(f"{'='*45}\n")


# ============================================================
# ケース1: アルゴリズム説明で使った「貪欲法が最適解を逃す」例
# ============================================================
EXAMPLE_ITEMS_SMALL = [
    Item("A", value=6,  weight=4),
    Item("B", value=5,  weight=3),
    Item("C", value=9,  weight=7),
]
EXAMPLE_CAPACITY_SMALL = 10

# ============================================================
# ケース2: やや大きめの標準的なテストケース
# ============================================================
EXAMPLE_ITEMS_MEDIUM = [
    Item("laptop",    value=150, weight=30),
    Item("camera",    value=35,  weight=5),
    Item("tablet",    value=80,  weight=15),
    Item("headphone", value=40,  weight=8),
    Item("book_set",  value=60,  weight=20),
    Item("clothes",   value=25,  weight=10),
    Item("charger",   value=20,  weight=4),
    Item("shoes",     value=30,  weight=12),
    Item("snacks",    value=10,  weight=5),
    Item("umbrella",  value=15,  weight=6),
]
EXAMPLE_CAPACITY_MEDIUM = 50


if __name__ == "__main__":
    # ケース1: 貪欲法が最適解を逃す例
    print("【ケース1】貪欲法が最適解を逃すケース")
    print("容量: 10")
    print("アイテム: A(v=6, w=4, d=1.50), B(v=5, w=3, d=1.67), C(v=9, w=7, d=1.29)")
    print("最適解: B+C = 価値14（後のDP実装で確認）")

    result_small = greedy_knapsack(EXAMPLE_ITEMS_SMALL, EXAMPLE_CAPACITY_SMALL)
    print_result(result_small, "貪欲法（ケース1）")

    # ケース2: 標準テストケース
    print("【ケース2】標準テストケース（10アイテム、容量50）")
    result_medium = greedy_knapsack(EXAMPLE_ITEMS_MEDIUM, EXAMPLE_CAPACITY_MEDIUM)
    print_result(result_medium, "貪欲法（ケース2）")

    # 各アイテムの密度も表示（貪欲法の選択根拠の可視化）
    print("【参考】全アイテムの価値密度ランキング（ケース2）")
    sorted_items = sorted(EXAMPLE_ITEMS_MEDIUM, key=lambda x: x.density, reverse=True)
    print(f"  {'名前':<12} {'価値':>6} {'重量':>6} {'密度':>8}")
    print(f"  {'-'*36}")
    for item in sorted_items:
        mark = "✓" if item in result_medium.selected_items else "✗"
        print(f"  {item.name:<12} {item.value:>6} {item.weight:>6} {item.density:>8.3f}  {mark}")