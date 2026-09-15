import z3


def build(instance):
    n, least, most = instance["n"], instance["m1"], instance["m2"]
    steps = [z3.Int(f"step_{i}") for i in range(n)]
    constraints = [s >= 0 for s in steps] + [s <= most for s in steps]
    constraints.append(z3.Sum(steps) == n)
    for i in range(n):
        constraints.append(z3.Or(steps[i] >= least, steps[i] == 0))
    for i in range(1, n):
        # Once a move is empty, every later one is too.
        constraints.append(z3.Implies(steps[i - 1] == 0,
                                      z3.And([steps[j] == 0 for j in range(i, n)])))
    return constraints, {"steps": steps}
