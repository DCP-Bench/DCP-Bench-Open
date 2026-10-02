# Finding celebrities: at a party, graph[i][j] = 1 when guest i knows guest j. A celebrity is a
# guest that everybody knows and who knows only celebrities; at least one celebrity is present.
from exact import Exact


def build(instance):
    graph = instance["graph"]
    n = len(graph)

    solver = Exact()

    # celebrities[i] = 1 when guest i is a celebrity
    celebrities = [f"celebrity_{i}" for i in range(n)]
    for name in celebrities:
        solver.addVariable(name, 0, 1)

    # num_celebrities is how many celebrities there are (at least one, at most everybody)
    solver.addVariable("num_celebrities", 1, n)
    solver.addConstraint([(1, name) for name in celebrities] + [(-1, "num_celebrities")],
                         True, 0, True, 0)

    # is_count[v] = 1 when there are exactly v celebrities. A celebrity i knows exactly
    # knows_count[i] guests and these must all be celebrities, so i is a celebrity only when
    # knows_count[i] equals the number of celebrities; the indicators express that equality.
    is_count = {v: f"num_celebrities_is_{v}" for v in range(1, n + 1)}
    for name in is_count.values():
        solver.addVariable(name, 0, 1)
    solver.addConstraint([(1, name) for name in is_count.values()], True, 1, True, 1)
    solver.addConstraint([(v, name) for v, name in is_count.items()] + [(-1, "num_celebrities")],
                         True, 0, True, 0)

    for i in range(n):
        known_by = sum(graph[j][i] for j in range(n))  # how many guests know guest i
        knows_count = sum(graph[i][j] for j in range(n))  # how many guests guest i knows
        if known_by == n and knows_count in is_count:
            # everybody knows i, so i is a celebrity exactly when i knows only celebrities, which
            # is when i's acquaintances number the same as all the celebrities
            solver.addConstraint([(1, celebrities[i]), (-1, is_count[knows_count])], True, 0, True, 0)
        else:
            # somebody does not know i, or i knows more guests than there are celebrities
            solver.addConstraint([(1, celebrities[i])], True, 0, True, 0)

    return solver, {"celebrities": celebrities}
