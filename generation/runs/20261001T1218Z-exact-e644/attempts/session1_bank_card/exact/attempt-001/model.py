# Bank card: find the 4-digit PIN abcd from three facts: no two digits are the same, the number cd
# is 3 times ab, and the number da is 2 times bc.
from exact import Exact


def build(instance):
    # This problem has no instance data. The PIN length and the two multiples belong to the
    # problem statement.
    digits = ["a", "b", "c", "d"]

    solver = Exact()
    for name in digits:
        solver.addVariable(name, 0, 9)

    # No two digits are the same. Exact has no all-different, so each digit gets one 0/1 indicator
    # per decimal value, and a value may be taken by at most one digit. Ten values per digit is
    # cheap.
    is_value = {name: [f"{name}_is_{v}" for v in range(10)] for name in digits}
    for name in digits:
        for indicator in is_value[name]:
            solver.addVariable(indicator, 0, 1)
        # the digit takes exactly one value
        solver.addConstraint([(1, indicator) for indicator in is_value[name]], True, 1, True, 1)
        # and the indicators say which: name = sum of value * indicator
        solver.addConstraint([(v, is_value[name][v]) for v in range(1, 10)] + [(-1, name)],
                             True, 0, True, 0)
    for v in range(10):
        solver.addConstraint([(1, is_value[name][v]) for name in digits], False, 0, True, 1)

    # The 2-digit number cd is 3 times the 2-digit number ab:  10c + d = 3 (10a + b)
    solver.addConstraint([(10, "c"), (1, "d"), (-30, "a"), (-3, "b")], True, 0, True, 0)
    # The 2-digit number da is 2 times the 2-digit number bc:  10d + a = 2 (10b + c)
    solver.addConstraint([(10, "d"), (1, "a"), (-20, "b"), (-2, "c")], True, 0, True, 0)

    return solver, {name: name for name in digits}
