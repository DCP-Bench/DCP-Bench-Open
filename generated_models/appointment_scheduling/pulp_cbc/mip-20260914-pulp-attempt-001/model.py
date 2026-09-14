import pulp


def build(instance):
    free = instance["m"]
    n = len(free)
    problem = pulp.LpProblem("appointment_scheduling", pulp.LpMinimize)
    booked = [[pulp.LpVariable(f"x_{i}_{j}", cat="Binary") for j in range(n)] for i in range(n)]
    for i in range(n):
        problem += pulp.lpSum(free[i][j] * booked[i][j] for j in range(n)) == 1
        problem += pulp.lpSum(booked[i]) == 1
        problem += pulp.lpSum(booked[j][i] for j in range(n)) == 1
    return problem, {"x": booked}
