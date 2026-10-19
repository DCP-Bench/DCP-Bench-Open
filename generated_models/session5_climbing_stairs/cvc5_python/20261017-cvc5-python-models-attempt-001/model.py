# Climbing stairs: a stair of n steps, moves of m1 to m2 steps at a time.
# Output steps[0..n-1]: the size of each move in order, or 0 for the moves
# after the top is reached.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    m1 = instance["m1"]
    m2 = instance["m2"]

    steps = [cz.Int(f"steps_{i}") for i in range(n)]
    constraints = []

    # Each move takes between m1 and m2 steps, or 0 if no move is made at that position.
    # Each move takes m1 to m2 steps at a time.
    for s in steps:
        constraints.append(cz.Or(s == 0, cz.And(s >= m1, s <= m2)))

    # The moves that are made come first, and the zeros after we reach the top.
    # 0 if no steps are taken at that move, i.e. after we reach the top of the stair.
    for i in range(n - 1):
        constraints.append(cz.Implies(steps[i] == 0, steps[i + 1] == 0))

    # The moves together climb exactly n steps.
    # Climb a stair of n steps.
    constraints.append(cz.Sum(steps) == n)

    return constraints, {"steps": steps}
