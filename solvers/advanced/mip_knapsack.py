"""
多次元ナップサック（プロジェクト選択）問題 - MIP（PuLP/HiGHS）

【アルゴリズム】
0/1整数計画問題として定式化し、HiGHSソルバーで厳密解を求める。
  max  Σ v_i * x_i
  s.t. Σ c_i * x_i <= budget
       Σ m_i * x_i <= manpower_limit
       x_i in {0, 1}

【特徴】
- 厳密解（最適解を保証）
- 制約の追加が容易（1行追加するだけ）
- 大規模問題でも実用的（Branch & Boundによる枝刈り）
- PuLPが数式に近い記述を可能にする
"""

import time
from pulp import (
    LpProblem, LpMaximize, LpVariable, lpSum, LpStatus, value, HiGHS
)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from solvers.advanced.greedy_advanced import (
    Project, MultiKnapsackResult, print_result,
    EXAMPLE_PROJECTS, EXAMPLE_BUDGET, EXAMPLE_MANPOWER,
)


def mip_knapsack(
    projects: list[Project],
    budget: int,
    manpower_limit: int,
) -> MultiKnapsackResult:
    """
    MIP（PuLP/HiGHS）で多次元ナップサック問題を解く（厳密解）。

    Parameters
    ----------
    projects : list[Project]
        プロジェクトリスト
    budget : int
        予算上限
    manpower_limit : int
        人員上限

    Returns
    -------
    MultiKnapsackResult

    Raises
    ------
    RuntimeError
        ソルバーが最適解を見つけられなかった場合
    """
    n = len(projects)

    # 問題定義
    prob = LpProblem("MultiDimKnapsack", LpMaximize)

    # 決定変数: x[i] in {0, 1}
    x = [LpVariable(f"x_{i}", cat="Binary") for i in range(n)]

    # 目的関数: Σ v_i * x_i を最大化
    prob += lpSum(projects[i].value * x[i] for i in range(n))

    # 制約1: 予算
    prob += lpSum(projects[i].cost * x[i] for i in range(n)) <= budget

    # 制約2: 人員
    prob += lpSum(projects[i].manpower * x[i] for i in range(n)) <= manpower_limit

    # 求解（msg=0でログ抑制）
    start = time.perf_counter()
    prob.solve(HiGHS(msg=False))
    elapsed = time.perf_counter() - start

    if LpStatus[prob.status] != "Optimal":
        raise RuntimeError(f"ソルバーが最適解を見つけられませんでした: {LpStatus[prob.status]}")

    # 選択プロジェクトの抽出（value()が1に近いものを選択済みとみなす）
    selected = [projects[i] for i in range(n) if value(x[i]) > 0.5]

    return MultiKnapsackResult(
        selected_projects=selected,
        total_value=int(round(value(prob.objective))),
        total_cost=sum(p.cost for p in selected),
        total_manpower=sum(p.manpower for p in selected),
        budget=budget,
        manpower_limit=manpower_limit,
        algorithm="MIP（HiGHS）",
        elapsed_time=elapsed,
    )


if __name__ == "__main__":
    print("【拡張問題】多次元ナップサック - MIP（PuLP/HiGHS）")
    print(f"予算上限: {EXAMPLE_BUDGET}、人員上限: {EXAMPLE_MANPOWER}")
    print(f"プロジェクト数: {len(EXAMPLE_PROJECTS)}")

    result = mip_knapsack(EXAMPLE_PROJECTS, EXAMPLE_BUDGET, EXAMPLE_MANPOWER)
    print_result(result)
    print(f"  求解時間: {result.elapsed_time:.4f} 秒\n")

    # 貪欲法との比較
    from solvers.advanced.greedy_advanced import greedy_advanced
    greedy_result = greedy_advanced(EXAMPLE_PROJECTS, EXAMPLE_BUDGET, EXAMPLE_MANPOWER)
    diff = result.total_value - greedy_result.total_value
    print(f"  貪欲法: {greedy_result.total_value} vs MIP: {result.total_value}", end="")
    if diff > 0:
        print(f"  → MIP が {diff} 改善")
    else:
        print("  → 同じ解（このケースでは貪欲法が最適解を出している）")