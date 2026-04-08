"""
多次元ナップサック（プロジェクト選択）問題 - 焼きなまし法（SA）

【アルゴリズム】
0/1ベクトルを状態として、ビット操作による近傍探索を行う。
高温時は悪化解も確率的に受理し局所最適を脱出、
低温時は良い解に収束させる。

【特徴】
- 最適解の保証なし（近似解）
- 大規模問題でも実用的な時間で動作
- 近傍操作: flip / swap / double-flip の3種
- 制約違反はペナルティ法で評価関数に組み込む
"""

import random
import math
import time
from dataclasses import dataclass, field
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from solvers.advanced.greedy_advanced import (
    Project, MultiKnapsackResult, print_result,
    EXAMPLE_PROJECTS, EXAMPLE_BUDGET, EXAMPLE_MANPOWER,
)


@dataclass
class SAConfig:
    """SAのハイパーパラメータ"""
    initial_temp: float = 100.0    # 初期温度
    cooling_rate: float = 0.995    # 冷却率（1ステップごとにT *= cooling_rate）
    min_temp: float = 0.1          # 終了温度
    penalty: float = 500.0         # 制約違反1単位あたりのペナルティ
    seed: int = 42


def _evaluate(
    state: list[int],
    projects: list[Project],
    budget: int,
    manpower_limit: int,
    penalty: float,
) -> float:
    """
    評価関数：総価値 - ペナルティ×制約超過量

    制約違反解にペナルティを与えることで、
    ソルバーが自然に実行可能解に誘導される。
    """
    total_value = 0
    total_cost = 0
    total_manpower = 0
    for i, selected in enumerate(state):
        if selected:
            total_value += projects[i].value
            total_cost += projects[i].cost
            total_manpower += projects[i].manpower

    cost_violation = max(0, total_cost - budget)
    manpower_violation = max(0, total_manpower - manpower_limit)

    return total_value - penalty * (cost_violation + manpower_violation)


def _is_feasible(
    state: list[int],
    projects: list[Project],
    budget: int,
    manpower_limit: int,
) -> bool:
    """制約を満たしているか判定"""
    total_cost = sum(projects[i].cost for i, s in enumerate(state) if s)
    total_manpower = sum(projects[i].manpower for i, s in enumerate(state) if s)
    return total_cost <= budget and total_manpower <= manpower_limit


def _neighbor(state: list[int], rng: random.Random) -> list[int]:
    """
    近傍操作：flip / swap / double-flip をランダムに選択

    - flip      : 1ビット反転（選択↔非選択）
    - swap      : 選択済み1個と未選択1個を交換
    - double-flip: 2ビット同時反転
    """
    n = len(state)
    new_state = state[:]
    op = rng.choice(["flip", "swap", "double_flip"])

    if op == "flip":
        i = rng.randrange(n)
        new_state[i] = 1 - new_state[i]

    elif op == "swap":
        selected = [i for i, s in enumerate(state) if s]
        unselected = [i for i, s in enumerate(state) if not s]
        if selected and unselected:
            i = rng.choice(selected)
            j = rng.choice(unselected)
            new_state[i], new_state[j] = 0, 1
        else:
            # swapできない場合はflipにフォールバック
            i = rng.randrange(n)
            new_state[i] = 1 - new_state[i]

    elif op == "double_flip":
        idxs = rng.sample(range(n), 2)
        for i in idxs:
            new_state[i] = 1 - new_state[i]

    return new_state


def sa_knapsack(
    projects: list[Project],
    budget: int,
    manpower_limit: int,
    config: SAConfig | None = None,
) -> MultiKnapsackResult:
    """
    焼きなまし法で多次元ナップサック問題を解く。

    Parameters
    ----------
    projects : list[Project]
        プロジェクトリスト
    budget : int
        予算上限
    manpower_limit : int
        人員上限
    config : SAConfig | None
        ハイパーパラメータ。Noneの場合はデフォルト値を使用

    Returns
    -------
    MultiKnapsackResult
    """
    if config is None:
        config = SAConfig()

    rng = random.Random(config.seed)
    n = len(projects)
    start = time.perf_counter()

    # 初期解：全て非選択（制約違反を避けるシンプルな出発点）
    current_state = [0] * n
    current_score = _evaluate(current_state, projects, budget, manpower_limit, config.penalty)

    # 実行可能解の中での最良値を別途追跡
    best_feasible_state = current_state[:]
    best_feasible_value = 0

    temp = config.initial_temp

    while temp > config.min_temp:
        new_state = _neighbor(current_state, rng)
        new_score = _evaluate(new_state, projects, budget, manpower_limit, config.penalty)

        delta = new_score - current_score

        # 改善解は必ず受理、悪化解は確率的に受理
        if delta >= 0 or rng.random() < math.exp(delta / temp):
            current_state = new_state
            current_score = new_score

        # 実行可能解の中での最良解を更新
        if _is_feasible(current_state, projects, budget, manpower_limit):
            feasible_value = sum(projects[i].value for i, s in enumerate(current_state) if s)
            if feasible_value > best_feasible_value:
                best_feasible_state = current_state[:]
                best_feasible_value = feasible_value

        temp *= config.cooling_rate

    elapsed = time.perf_counter() - start

    selected = [projects[i] for i, s in enumerate(best_feasible_state) if s]

    return MultiKnapsackResult(
        selected_projects=selected,
        total_value=sum(p.value for p in selected),
        total_cost=sum(p.cost for p in selected),
        total_manpower=sum(p.manpower for p in selected),
        budget=budget,
        manpower_limit=manpower_limit,
        algorithm="SA（焼きなまし法）",
        elapsed_time=elapsed,
    )


if __name__ == "__main__":
    print("【拡張問題】多次元ナップサック - SA（焼きなまし法）")
    print(f"予算上限: {EXAMPLE_BUDGET}、人員上限: {EXAMPLE_MANPOWER}")
    print(f"プロジェクト数: {len(EXAMPLE_PROJECTS)}\n")

    result = sa_knapsack(EXAMPLE_PROJECTS, EXAMPLE_BUDGET, EXAMPLE_MANPOWER)
    print_result(result)
    print(f"  求解時間: {result.elapsed_time:.4f} 秒\n")

    # 3手法比較
    from solvers.advanced.greedy_advanced import greedy_advanced
    from solvers.advanced.mip_knapsack import mip_knapsack

    greedy_result = greedy_advanced(EXAMPLE_PROJECTS, EXAMPLE_BUDGET, EXAMPLE_MANPOWER)
    mip_result = mip_knapsack(EXAMPLE_PROJECTS, EXAMPLE_BUDGET, EXAMPLE_MANPOWER)

    print("【3手法比較】")
    print(f"  {'手法':<16} {'総価値':>6} {'予算使用率':>10} {'人員使用率':>10} {'時間(秒)':>10}")
    print(f"  {'-'*56}")
    for r in [greedy_result, mip_result, result]:
        print(f"  {r.algorithm:<16} {r.total_value:>6} "
              f"{r.budget_utilization:>10.1%} "
              f"{r.manpower_utilization:>10.1%} "
              f"{r.elapsed_time:>10.4f}")

    print(f"\n  MIP最適値との差: 貪欲法={mip_result.total_value - greedy_result.total_value}, "
          f"SA={mip_result.total_value - result.total_value}")