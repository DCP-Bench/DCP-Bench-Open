# Clock triplets: arrange the numbers 1 to 12 on a clock face so that no three
# neighbouring numbers add up to more than 21.
from exact import Exact


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    n = 12
    solver = Exact()
    # x[i] = the number at position i of the clock
    x = [f"x_{i}" for i in range(n)]
    for name in x:
        solver.addVariable(name, 1, n)

    # every number appears once: indicators say which number a position holds, and
    # each number is used exactly once
    is_ = [[f"x_{i}_is_{v}" for v in range(1, n + 1)] for i in range(n)]
    for i in range(n):
        for name in is_[i]:
            solver.addVariable(name, 0, 1)
        solver.addConstraint([(1, name) for name in is_[i]], True, 1, True, 1)
        solver.addConstraint([(v, is_[i][v - 1]) for v in range(1, n + 1)] + [(-1, x[i])], True, 0, True, 0)
    for v in range(n):
        solver.addConstraint([(1, is_[i][v]) for i in range(n)], True, 1, True, 1)

    # no three neighbouring positions (going round the clock) add up to more than 21
    for i in range(n):
        solver.addConstraint([(1, x[i]), (1, x[(i + 1) % n]), (1, x[(i + 2) % n])], False, 0, True, 21)

    return solver, {"x": x}
