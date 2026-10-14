# Giant cat army riddle: start from [0] and extend the list by adding 5, adding
# 7 or taking a square root, so that all numbers are different integers of at
# most 60, the list contains 2, then 10, then 14 (in that order), and it ends
# with 14 after exactly 24 numbers.
from exact import Exact

# The riddle fixes these numbers, so they are mirrored here.
MAX_VALUE = 60  # largest number allowed in the list
LENGTH = 24  # number of entries in the list
GOAL = 14  # the last entry


def build(instance):
    solver = Exact()
    x = [f"x_{i}" for i in range(LENGTH)]
    # is_[i][v] is 1 exactly when the i-th number is v
    is_ = [{} for _ in range(LENGTH)]
    for i in range(LENGTH):
        solver.addVariable(x[i], 0, MAX_VALUE)
        for v in range(MAX_VALUE + 1):
            is_[i][v] = f"is_{i}_{v}"
            solver.addVariable(is_[i][v], 0, 1)
        solver.addConstraint([(1, is_[i][v]) for v in range(MAX_VALUE + 1)], True, 1, True, 1)
        solver.addConstraint([(v, is_[i][v]) for v in range(1, MAX_VALUE + 1)] + [(-1, x[i])], True, 0, True, 0)

    # all numbers are different: each value appears at most once
    for v in range(MAX_VALUE + 1):
        solver.addConstraint([(1, is_[i][v]) for i in range(LENGTH)], False, 0, True, 1)

    # the list starts with 0 and ends with 14
    solver.addConstraint([(1, is_[0][0])], True, 1, True, 1)
    solver.addConstraint([(1, is_[LENGTH - 1][GOAL])], True, 1, True, 1)

    # each number follows the previous one by adding 5, adding 7, or taking the
    # square root (the previous number is the square of the next one): if the
    # i-th number is v, the next one is one of v + 5, v + 7 and the s with s * s = v
    for i in range(LENGTH - 1):
        for v in range(MAX_VALUE + 1):
            successors = [w for w in (v + 5, v + 7) if w <= MAX_VALUE]
            root = int(v ** 0.5)
            if root * root == v:
                successors.append(root)
            solver.addConstraint([(1, is_[i + 1][w]) for w in successors] + [(-1, is_[i][v])], True, 0)

    # the list contains 2 and later 10: 10 appears, and wherever it does, 2 comes earlier
    solver.addConstraint([(1, is_[j][10]) for j in range(LENGTH)], True, 1)
    for j in range(1, LENGTH):
        solver.addConstraint([(1, is_[i][2]) for i in range(1, j)] + [(-1, is_[j][10])], True, 0)

    return solver, {"x": x}
