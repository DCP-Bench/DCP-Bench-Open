import pulp


def build(instance):
    n, adjacency = instance["n"], instance["adj"]
    problem = pulp.LpProblem("maximum_clique", pulp.LpMaximize)
    chosen = [pulp.LpVariable(f"c_{i}", cat="Binary") for i in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if adjacency[i][j] == 0:
                problem += chosen[i] + chosen[j] <= 1
    problem += pulp.lpSum(chosen)
    return problem, {"c": chosen}
