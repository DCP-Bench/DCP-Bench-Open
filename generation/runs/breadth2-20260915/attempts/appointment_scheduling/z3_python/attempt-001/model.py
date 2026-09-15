import z3


def build(instance):
    free = instance["m"]
    n = len(free)
    booked = [[z3.Bool(f"x_{i}_{j}") for j in range(n)] for i in range(n)]
    taken = [[z3.If(booked[i][j], 1, 0) for j in range(n)] for i in range(n)]
    constraints = []
    for i in range(n):
        constraints.append(z3.Sum([free[i][j] * taken[i][j] for j in range(n)]) == 1)
        constraints.append(z3.Sum(taken[i]) == 1)
        constraints.append(z3.Sum([taken[j][i] for j in range(n)]) == 1)
    return constraints, {"x": booked}
