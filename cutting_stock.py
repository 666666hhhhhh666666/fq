# coding: utf-8
import argparse
from ortools.sat.python import cp_model

def solve_cutting_stock(W, widths, demands):
    model = cp_model.CpModel()
    n = len(widths)
    # 生成模式（简化示例）
    patterns = []
    def dfs(idx, cur, used):
        if idx == n:
            if 0 < used <= W:
                patterns.append(cur.copy())
            return
        maxc = W // widths[idx]
        for c in range(maxc + 1):
            cur.append(c)
            dfs(idx+1, cur, used + c*widths[idx])
            cur.pop()
    dfs(0, [], 0)

    x = [model.NewIntVar(0, sum(demands), f"x{p}") for p in range(len(patterns))]
    for i in range(n):
        model.Add(sum(x[p] * patterns[p][i] for p in range(len(patterns))) >= demands[i])
    total_waste = sum(x[p] * (W - sum(patterns[p][i]*widths[i] for i in range(n))) for p in range(len(patterns)))
    model.Minimize(total_waste)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10
    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError("No feasible solution found")
    used = {p: solver.Value(x[p]) for p in range(len(patterns)) if solver.Value(x[p]) > 0}
    total = sum(used[p] * (W - sum(patterns[p][i]*widths[i] for i in range(n))) for p in used)
    rolls = sum(used.values())
    rate = total / (W * rolls)
    return used, total, rate

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="一维切割库存优化")
    parser.add_argument("--W",  type=int,       required=True, help="大卷宽度")
    parser.add_argument("--widths", nargs="+", type=int, required=True, help="小卷宽度列表")
    parser.add_argument("--demands", nargs="+",type=int, required=True, help="需求数量列表")
    args = parser.parse_args()

    patterns, waste, rate = solve_cutting_stock(args.W, args.widths, args.demands)
    print("切割方案:", patterns)
    print(f"总浪费: {waste}  损耗率: {rate:.2%}")
