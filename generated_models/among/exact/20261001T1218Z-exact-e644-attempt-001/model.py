# Among: find an array x of n values in 0..7 such that exactly m of its entries take a value
# that appears in the list v.
from exact import Exact


def build(instance):
    n = instance["n"]  # length of x
    m = instance["m"]  # how many entries of x must take one of the values in v
    v = instance["v"]  # the values to be "among"
    # the reference fixes the value range of every entry of x to 0..7 (a problem constant)
    max_value = 7

    solver = Exact()

    x = [f"x_{i}" for i in range(n)]
    # is_value[i][a] = 1 when x[i] == a. Exact has no counting constraint, so the entries
    # that hit v are counted through these 0/1 indicators; the domain 0..7 keeps them few.
    is_value = [[f"x_{i}_is_{a}" for a in range(max_value + 1)] for i in range(n)]
    for i in range(n):
        solver.addVariable(x[i], 0, max_value)
        for name in is_value[i]:
            solver.addVariable(name, 0, 1)
        # each entry takes exactly one value
        solver.addConstraint([(1, name) for name in is_value[i]], True, 1, True, 1)
        solver.addConstraint([(a, is_value[i][a]) for a in range(1, max_value + 1)] + [(-1, x[i])],
                             True, 0, True, 0)

    # exactly m entries take a value from v. The reference sums x[i] == j over every entry i
    # and every listed value j, so a value listed twice counts twice; the coefficient is the
    # number of times a is listed in v.
    hits = [(v.count(a), is_value[i][a]) for i in range(n) for a in range(max_value + 1) if v.count(a)]
    solver.addConstraint(hits, True, m, True, m)

    return solver, {"x": x}
