import pulp


def build(instance):
    n, least, most = instance["n"], instance["m1"], instance["m2"]
    moves = range(n)
    problem = pulp.LpProblem("climbing_stairs", pulp.LpMinimize)
    steps = [pulp.LpVariable(f"step_{i}", 0, most, cat="Integer") for i in moves]
    taken = [pulp.LpVariable(f"taken_{i}", cat="Binary") for i in moves]
    problem += pulp.lpSum(steps) == n
    for i in moves:
        problem += steps[i] >= least * taken[i]
        problem += steps[i] <= most * taken[i]
    for i in range(1, n):
        # Once a move is empty, every later one is too.
        problem += taken[i] <= taken[i - 1]
    return problem, {"steps": steps}
