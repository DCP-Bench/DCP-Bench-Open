# Fibonacci even: add up the even-valued terms of the Fibonacci sequence that do
# not exceed four million.
from exact import Exact

N = 35  # terms considered: f_1 .. f_35, the largest is below 10 million
LIMIT = 4000000


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    solver = Exact()
    # f[i] = the i-th Fibonacci number: f_0 = 0, f_1 = f_2 = 1, then the sum of the previous two
    f = [f"f_{i}" for i in range(N + 1)]
    for name in f:
        solver.addVariable(name, 0, 10 ** 7)
    solver.addConstraint([(1, f[0])], True, 0, True, 0)
    solver.addConstraint([(1, f[1])], True, 1, True, 1)
    solver.addConstraint([(1, f[2])], True, 1, True, 1)
    for i in range(3, N + 1):
        solver.addConstraint([(1, f[i]), (-1, f[i - 1]), (-1, f[i - 2])], True, 0, True, 0)

    # taken[i] = 1 when f_i is even and below the limit; taken[i] * f[i] is what it adds to the sum
    parts = []
    for i in range(1, N + 1):
        # half[i] and odd[i] write f_i = 2 * half + odd, so f_i is even when odd is 0
        half, odd = f"half_{i}", f"odd_{i}"
        solver.addVariable(half, 0, 5 * 10 ** 6)
        solver.addVariable(odd, 0, 1)
        solver.addConstraint([(2, half), (1, odd), (-1, f[i])], True, 0, True, 0)
        # below[i] = 1 exactly when f_i < 4000000
        below, taken, part = f"below_{i}", f"taken_{i}", f"part_{i}"
        solver.addVariable(below, 0, 1)
        solver.addReification(below, True, [(-1, f[i])], -(LIMIT - 1))
        # taken = below and not odd
        solver.addVariable(taken, 0, 1)
        solver.addConstraint([(1, taken), (-1, below)], False, 0, True, 0)
        solver.addConstraint([(1, taken), (1, odd)], False, 0, True, 1)
        solver.addConstraint([(1, taken), (-1, below), (1, odd)], True, 0)
        solver.addVariable(part, 0, 10 ** 7)
        solver.addMultiplication([taken, f[i]], True, part, True, part)
        parts.append(part)

    # res = the sum of the even terms below the limit
    solver.addVariable("res", 0, 10 ** 8)
    solver.addConstraint([(1, part) for part in parts] + [(-1, "res")], True, 0, True, 0)

    return solver, {"res": "res"}
