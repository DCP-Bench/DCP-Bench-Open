import pulp


def build(instance):
    """Added corners: digits 1..8 around a ring, each square the sum of its two
    adjoining circles. Reading order is a b c / d _ e / f g h.
    """
    del instance

    n = 8
    problem = pulp.LpProblem("corners", pulp.LpMinimize)
    # All-different over 1..8 as a permutation matrix, with positions reading
    # the digit back off it.
    pick = pulp.LpVariable.dicts("pick", (range(n), range(1, n + 1)),
                                 cat="Binary")
    positions = [pulp.LpVariable(f"p{i}", 1, n, cat="Integer")
                 for i in range(n)]
    for i in range(n):
        problem += pulp.lpSum(pick[i][v] for v in range(1, n + 1)) == 1
        problem += positions[i] == pulp.lpSum(v * pick[i][v]
                                              for v in range(1, n + 1))
    for v in range(1, n + 1):
        problem += pulp.lpSum(pick[i][v] for i in range(n)) == 1

    for square, first, second in ((1, 0, 2), (3, 0, 5), (4, 2, 7), (6, 5, 7)):
        problem += positions[square] == positions[first] + positions[second]

    return problem, {"positions": positions}
