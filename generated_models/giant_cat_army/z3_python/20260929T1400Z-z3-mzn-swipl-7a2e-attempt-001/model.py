# Giant cat army riddle: start from [0] and extend the list by adding 5, adding
# 7 or taking a square root, so that all numbers are different integers of at
# most 60, the list contains 2, then 10, then 14 (in that order), and it ends
# with 14 after exactly 24 numbers.
import z3

# The riddle fixes these numbers, so they are mirrored here.
MAX_VALUE = 60  # largest number allowed in the list
LENGTH = 24  # number of entries in the list
GOAL = 14  # the last entry


def build(instance):
    solver = z3.Solver()

    # x[i] = the i-th number of the list
    x = [z3.Int(f"x_{i}") for i in range(LENGTH)]
    for value in x:
        solver.add(value >= 0, value <= MAX_VALUE)

    # all numbers are different
    solver.add(z3.Distinct(x))

    # the list starts with 0 and ends with 14
    solver.add(x[0] == 0)
    solver.add(x[LENGTH - 1] == GOAL)

    # each number follows the previous one by adding 5, adding 7, or taking the
    # square root (the previous number x[i] is the square of the next x[i+1])
    for i in range(LENGTH - 1):
        solver.add(z3.Or(x[i + 1] == x[i] + 5, x[i + 1] == x[i] + 7, x[i] == x[i + 1] * x[i + 1]))

    # the list contains 2 and later 10 (and, as it ends with it, 14 after both)
    solver.add(z3.Or([z3.And(x[i] == 2, x[j] == 10) for i in range(1, LENGTH) for j in range(i + 1, LENGTH)]))

    return solver, {"x": x}
