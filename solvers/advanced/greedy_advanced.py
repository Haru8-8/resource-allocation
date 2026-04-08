"""
多次元ナップサック（プロジェクト選択）問題 - 貪欲法

【アルゴリズム】
複数制約を重み付き正規化スコアに集約し、スコア降順に貪欲選択する。

【特徴】
- 時間計算量: O(n log n)
- 最適解の保証なし（近似解）
- 重み付けパラメータαの設定が結果に影響する
- 多次元でもDPのような次元爆発が起きない
"""

from dataclasses import dataclass, field


@dataclass
class Project:
    """多次元ナップサック問題の1プロジェクト"""
    name: str
    value: int       # 期待利益
    cost: int        # 必要予算
    manpower: int    # 必要人員

    def score(self, max_cost: float, max_manpower: float, alpha: float = 0.5) -> float:
        """
        重み付き正規化スコア。

        Parameters
        ----------
        max_cost : float
            正規化用の予算最大値（全プロジェクト中の最大cost）
        max_manpower : float
            正規化用の人員最大値（全プロジェクト中の最大manpower）
        alpha : float
            予算への重み（0〜1）。0.5で予算・人員を等ウェイト

        Notes
        -----
        正規化することで単位の異なる制約を同一スケールで扱う。
        ただしαの設定は恣意的であり、最適性の保証はない。
        """
        norm_cost = self.cost / max_cost if max_cost > 0 else 0
        norm_manpower = self.manpower / max_manpower if max_manpower > 0 else 0
        denominator = alpha * norm_cost + (1 - alpha) * norm_manpower
        if denominator == 0:
            return float("inf")
        return self.value / denominator


@dataclass
class MultiKnapsackResult:
    """多次元ナップサック問題の解"""
    selected_projects: list[Project]
    total_value: int
    total_cost: int
    total_manpower: int
    budget: int
    manpower_limit: int
    algorithm: str = ""
    elapsed_time: float = 0.0

    @property
    def budget_utilization(self) -> float:
        return self.total_cost / self.budget

    @property
    def manpower_utilization(self) -> float:
        return self.total_manpower / self.manpower_limit


def greedy_advanced(
    projects: list[Project],
    budget: int,
    manpower_limit: int,
    alpha: float = 0.5,
) -> MultiKnapsackResult:
    """
    貪欲法で多次元ナップサック問題を解く。

    Parameters
    ----------
    projects : list[Project]
        プロジェクトリスト
    budget : int
        予算上限
    manpower_limit : int
        人員上限
    alpha : float
        スコア計算時の予算重み（0〜1）

    Returns
    -------
    MultiKnapsackResult
    """
    max_cost = max(p.cost for p in projects)
    max_manpower = max(p.manpower for p in projects)

    sorted_projects = sorted(
        projects,
        key=lambda p: p.score(max_cost, max_manpower, alpha),
        reverse=True,
    )

    selected: list[Project] = []
    remaining_budget = budget
    remaining_manpower = manpower_limit

    for project in sorted_projects:
        if project.cost <= remaining_budget and project.manpower <= remaining_manpower:
            selected.append(project)
            remaining_budget -= project.cost
            remaining_manpower -= project.manpower

    return MultiKnapsackResult(
        selected_projects=selected,
        total_value=sum(p.value for p in selected),
        total_cost=sum(p.cost for p in selected),
        total_manpower=sum(p.manpower for p in selected),
        budget=budget,
        manpower_limit=manpower_limit,
        algorithm="貪欲法",
    )


def print_result(result: MultiKnapsackResult) -> None:
    """結果を整形して表示する"""
    print(f"\n{'='*55}")
    print(f"  {result.algorithm} - 結果")
    print(f"{'='*55}")
    print(f"  総価値    : {result.total_value}")
    print(f"  予算使用  : {result.total_cost} / {result.budget}"
          f"  ({result.budget_utilization:.1%})")
    print(f"  人員使用  : {result.total_manpower} / {result.manpower_limit}"
          f"  ({result.manpower_utilization:.1%})")
    print(f"\n  選択プロジェクト ({len(result.selected_projects)}件):")
    print(f"  {'名前':<16} {'価値':>6} {'予算':>6} {'人員':>6}")
    print(f"  {'-'*38}")
    for p in result.selected_projects:
        print(f"  {p.name:<16} {p.value:>6} {p.cost:>6} {p.manpower:>6}")
    print(f"{'='*55}\n")


# ============================================================
# テストデータ（MIP・SAと共通で使用）
# ============================================================
EXAMPLE_PROJECTS = [
    Project("AI開発",       value=120, cost=50, manpower=8),
    Project("Web刷新",      value=80,  cost=30, manpower=5),
    Project("DB移行",       value=60,  cost=20, manpower=4),
    Project("モバイルApp",  value=100, cost=45, manpower=7),
    Project("セキュリティ", value=70,  cost=25, manpower=3),
    Project("分析基盤",     value=90,  cost=40, manpower=6),
    Project("UI改善",       value=40,  cost=15, manpower=2),
    Project("API統合",      value=55,  cost=20, manpower=3),
    Project("クラウド移行", value=110, cost=55, manpower=9),
    Project("自動化ツール", value=65,  cost=25, manpower=4),
    Project("監視強化",     value=45,  cost=18, manpower=2),
    Project("データ品質",   value=50,  cost=22, manpower=3),
]
EXAMPLE_BUDGET = 120
EXAMPLE_MANPOWER = 20


if __name__ == "__main__":
    print("【拡張問題】多次元ナップサック - 貪欲法")
    print(f"予算上限: {EXAMPLE_BUDGET}、人員上限: {EXAMPLE_MANPOWER}")
    print(f"プロジェクト数: {len(EXAMPLE_PROJECTS)}")

    result = greedy_advanced(EXAMPLE_PROJECTS, EXAMPLE_BUDGET, EXAMPLE_MANPOWER)
    print_result(result)

    # αの影響を確認
    print("【参考】αによるスコア変化（α=0.3 / 0.5 / 0.7）")
    for alpha in [0.3, 0.5, 0.7]:
        r = greedy_advanced(EXAMPLE_PROJECTS, EXAMPLE_BUDGET, EXAMPLE_MANPOWER, alpha=alpha)
        names = [p.name for p in r.selected_projects]
        print(f"  α={alpha}: 価値={r.total_value}  選択={names}")