# Hardy's 1729 square: find four different numbers a, b, c, d between 1 and 100 such that
# a^2 + b^2 = c^2 + d^2.
from exact import Exact


def build(instance):
    # This problem has no instance data. The range 1..100 belongs to the problem statement.
    range_min, range_max = 1, 100
    numbers = ["a", "b", "c", "d"]
    values = range(range_min, range_max + 1)

    solver = Exact()
    for name in numbers:
        solver.addVariable(name, range_min, range_max)

    # Exact's constraints are linear, so each number gets one 0/1 indicator per value in the
    # range: is_value[name][v] = 1 when the number equals v. A square is then a sum of v * v
    # over the indicators, and "all different" is "each value is taken at most once".
    is_value = {name: {v: f"{name}_is_{v}" for v in values} for name in numbers}
    for name in numbers:
        for v in values:
            solver.addVariable(is_value[name][v], 0, 1)
        solver.addConstraint([(1, is_value[name][v]) for v in values], True, 1, True, 1)
        solver.addConstraint([(v, is_value[name][v]) for v in values] + [(-1, name)],
                             True, 0, True, 0)

    # The four numbers are all different.
    for v in values:
        solver.addConstraint([(1, is_value[name][v]) for name in numbers], False, 0, True, 1)

    # The sum of the squares of the two first numbers equals the sum of the squares of the other
    # two:  a^2 + b^2 - c^2 - d^2 = 0
    squares = [(v * v, is_value["a"][v]) for v in values] + \
              [(v * v, is_value["b"][v]) for v in values] + \
              [(-v * v, is_value["c"][v]) for v in values] + \
              [(-v * v, is_value["d"][v]) for v in values]
    solver.addConstraint(squares, True, 0, True, 0)

    return solver, {name: name for name in numbers}
