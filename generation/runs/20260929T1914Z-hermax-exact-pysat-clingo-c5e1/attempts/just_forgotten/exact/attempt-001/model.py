# Just forgotten: Joe's account number uses each digit 0 to n-1 once. In each of
# several tried sets exactly some given number of digits are in the right place.
from exact import Exact


def build(instance):
    sets = instance["sets"]  # the digit sequences Joe tried
    num_correct = instance["num_correct_digits"]  # digits in the right place in each set
    n = len(sets[0])

    solver = Exact()
    # is_[i][d] = 1 when position i of the account number holds the digit d
    is_ = [[f"is_{i}_{d}" for d in range(n)] for i in range(n)]
    for i in range(n):
        for name in is_[i]:
            solver.addVariable(name, 0, 1)
        # a position holds exactly one digit
        solver.addConstraint([(1, name) for name in is_[i]], True, 1, True, 1)
    # each digit is used exactly once
    for d in range(n):
        solver.addConstraint([(1, is_[i][d]) for i in range(n)], True, 1, True, 1)

    # x[i] = the digit at position i
    x = [f"x_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(x[i], 0, n - 1)
        solver.addConstraint([(d, is_[i][d]) for d in range(1, n)] + [(-1, x[i])], True, 0, True, 0)

    # every tried set has exactly num_correct digits in the position they have in the number
    for tried in sets:
        solver.addConstraint([(1, is_[i][tried[i]]) for i in range(n)], True, num_correct, True, num_correct)

    return solver, {"x": x}
