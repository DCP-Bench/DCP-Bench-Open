"""Project Euler 2: the sum of the even-valued Fibonacci terms that do not exceed four
million.
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data. As in the reference: 35 terms, each in 0..10^7, the
    # sum in 0..10^8, and the threshold 4 000 000 from the statement.
    n = 35
    f_max = 10000000
    res_max = 100000000
    limit = 4000000
    terms = range(1, n + 1)

    model = Model("fibonacci_even")
    # The product below uses a bound of 10^7; with CPLEX's default integrality tolerance
    # (1e-5) a "zero" binary could carry up to 100 through it, so integrality is exact.
    model.parameters.mip.tolerances.integrality = 0

    # f[i] is the i-th Fibonacci term: 0, 1, 1, then each term the sum of the two before.
    f = [model.integer_var(0, f_max, name=f"f_{i}") for i in range(n + 1)]
    model.add_constraint(f[0] == 0)
    model.add_constraint(f[1] == 1)
    model.add_constraint(f[2] == 1)
    for i in range(3, n + 1):
        model.add_constraint(f[i] == f[i - 1] + f[i - 2])

    # x[i] is 1 exactly when f[i] is even and below four million.
    res_terms = []
    for i in terms:
        # f[i] = 2 * half + odd: odd is 1 when f[i] is odd.
        half = model.integer_var(0, f_max // 2, name=f"half_{i}")
        odd = model.binary_var(name=f"odd_{i}")
        model.add_constraint(f[i] == 2 * half + odd)
        # below is 1 exactly when f[i] < 4 000 000.
        below = model.binary_var(name=f"below_{i}")
        model.add_equivalence(below, f[i] <= limit - 1)
        # x = (not odd) and below.
        x = model.binary_var(name=f"x_{i}")
        model.add_constraint(x <= 1 - odd)
        model.add_constraint(x <= below)
        model.add_constraint(x >= below - odd)
        # counted = x * f[i]: the term if it is counted, else 0 (binary times bounded integer).
        counted = model.integer_var(0, f_max, name=f"counted_{i}")
        model.add_constraint(counted <= f_max * x)
        model.add_constraint(counted <= f[i])
        model.add_constraint(counted >= f[i] - f_max * (1 - x))
        res_terms.append(counted)

    # res is the sum of the counted terms.
    res = model.integer_var(0, res_max, name="res")
    model.add_constraint(res == model.sum(res_terms))

    return model, {"res": res}
