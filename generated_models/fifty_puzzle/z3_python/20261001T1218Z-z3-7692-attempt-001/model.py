# Fifty puzzle: choose which dummies to knock over so that the numbers on them add up to
# exactly the target sum.
import z3


def build(instance):
    target_sum = instance["target_sum"]  # sum that wins the prize
    values = instance["values"]          # the number on each dummy
    n = len(values)

    # dummies[i] is true if dummy i is knocked over.
    dummies = [z3.Bool(f"dummies_{i}") for i in range(n)]

    solver = z3.Solver()

    # The numbers on the knocked-over dummies add up to exactly the target sum.
    # A pseudo-Boolean equality over the weights is used because every term is a
    # 0/1 choice times a constant.
    solver.add(z3.PbEq([(dummies[i], values[i]) for i in range(n)], target_sum))

    return solver, {"dummies": dummies}
