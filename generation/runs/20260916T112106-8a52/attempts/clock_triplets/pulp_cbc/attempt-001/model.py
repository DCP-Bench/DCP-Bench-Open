import pulp


def build(instance):
    """Clock triplets: rearrange 1..12 around a clock face so that no three
    adjacent numbers sum above 21.
    """
    del instance

    n = 12
    problem = pulp.LpProblem("clock", pulp.LpMinimize)
    pick = pulp.LpVariable.dicts("pick", (range(n), range(1, n + 1)),
                                 cat="Binary")
    x = [pulp.LpVariable(f"x{i}", 1, n, cat="Integer") for i in range(n)]
    for i in range(n):
        problem += pulp.lpSum(pick[i][v] for v in range(1, n + 1)) == 1
        problem += x[i] == pulp.lpSum(v * pick[i][v] for v in range(1, n + 1))
    for v in range(1, n + 1):
        problem += pulp.lpSum(pick[i][v] for i in range(n)) == 1

    # Triplets wrap around the face; the reference caps the largest at 21.
    for i in range(n):
        problem += x[i] + x[(i - 1) % n] + x[(i - 2) % n] <= 21

    return problem, {"x": x}
