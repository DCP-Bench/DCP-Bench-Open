# Magic sequence: find x_0 .. x_{n-1}, each between 0 and n-1, such that the number i occurs
# exactly x_i times in the sequence, for every i.
from exact import Exact


def build(instance):
    n = instance["n"]  # length of the sequence; every entry is a count, so it lies in 0..n-1

    solver = Exact()

    x = [f"x_{i}" for i in range(n)]
    # is_value[j][i] = 1 when x[j] == i. Exact has no counting constraint, so occurrences of a
    # value are counted by summing these indicators; the domain 0..n-1 is small enough for that.
    is_value = [[f"x_{j}_is_{i}" for i in range(n)] for j in range(n)]
    for j in range(n):
        solver.addVariable(x[j], 0, n - 1)
        for name in is_value[j]:
            solver.addVariable(name, 0, 1)
        # each entry takes exactly one value
        solver.addConstraint([(1, name) for name in is_value[j]], True, 1, True, 1)
        # x[j] is the value whose indicator is set
        solver.addConstraint([(i, is_value[j][i]) for i in range(1, n)] + [(-1, x[j])], True, 0, True, 0)

    # the number i occurs exactly x_i times in the sequence
    for i in range(n):
        solver.addConstraint([(1, is_value[j][i]) for j in range(n)] + [(-1, x[i])], True, 0, True, 0)

    return solver, {"x": x}
