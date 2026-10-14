# Divisible by 1 through 9: find a 10-digit number that uses each digit 0-9 once
# and whose first n digits form a number divisible by n, for n = 1 to 10.
from exact import Exact


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    n = 10
    solver = Exact()
    # digits[i] = the i-th digit from the left
    digits = [f"digit_{i}" for i in range(n)]
    for name in digits:
        solver.addVariable(name, 0, 9)

    # every digit is used once: indicators say which digit a position holds
    is_ = [[f"digit_{i}_is_{d}" for d in range(10)] for i in range(n)]
    for i in range(n):
        for name in is_[i]:
            solver.addVariable(name, 0, 1)
        solver.addConstraint([(1, name) for name in is_[i]], True, 1, True, 1)
        solver.addConstraint([(d, is_[i][d]) for d in range(1, 10)] + [(-1, digits[i])], True, 0, True, 0)
    for d in range(10):
        solver.addConstraint([(1, is_[i][d]) for i in range(n)], True, 1, True, 1)

    # prefix[i] = the number formed by the first i + 1 digits: 10 times the previous one plus the digit
    prefix = [f"prefix_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(prefix[i], 0, 10 ** (i + 1) - 1)
    solver.addConstraint([(1, prefix[0]), (-1, digits[0])], True, 0, True, 0)
    for i in range(1, n):
        solver.addConstraint([(1, prefix[i]), (-10, prefix[i - 1]), (-1, digits[i])], True, 0, True, 0)

    # the first i + 1 digits form a number divisible by i + 1: prefix[i] = (i + 1) * multiple[i]
    for i in range(n):
        multiple = f"multiple_{i}"
        solver.addVariable(multiple, 0, (10 ** (i + 1) - 1) // (i + 1))
        solver.addConstraint([(1, prefix[i]), (-(i + 1), multiple)], True, 0, True, 0)

    return solver, {"number": prefix[n - 1]}
