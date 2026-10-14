# The 50 puzzle: choose which dummies to knock over so that the numbers on the knocked-over
# dummies add up to exactly the target sum.
from exact import Exact


def build(instance):
    target_sum = instance["target_sum"]
    values = instance["values"]  # the number on each dummy
    n = len(values)

    solver = Exact()

    # dummies[i] = 1 when dummy i is knocked over
    dummies = [f"dummy_{i}" for i in range(n)]
    for name in dummies:
        solver.addVariable(name, 0, 1)

    # the numbers on the knocked-over dummies sum to exactly the target
    solver.addConstraint([(v, d) for v, d in zip(values, dummies) if v], True, target_sum, True, target_sum)

    return solver, {"dummies": dummies}
