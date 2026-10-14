"""KenKen: fill an n-by-n grid with 1..n so that every row and every column holds different
numbers, and every cage meets its clue. A two-cell cage with clue res holds a and b with
a + b, a * b, a - b, b - a, a / b or b / a equal to res; a larger (or single-cell) cage has
its numbers adding up to res or multiplying to res.

The model reports the filled grid.
"""
from docplex.mp.model import Model


def prime_factors(value):
    """The exponent of each prime in value, as a dict."""
    factors = {}
    p = 2
    while p * p <= value:
        while value % p == 0:
            factors[p] = factors.get(p, 0) + 1
            value //= p
        p += 1
    if value > 1:
        factors[value] = factors.get(value, 0) + 1
    return factors


def build(instance):
    n = instance["n"]              # size of the grid
    cages = instance["problem"]    # cages as [res, [[row, col], ...]], 1-based

    cells = range(n)
    values = range(1, n + 1)

    model = Model("kenken")

    # has[i, j, v] is 1 when cell (i, j) holds v; every cell holds one number.
    has = {(i, j, v): model.binary_var(name=f"has_{i}_{j}_{v}") for i in cells for j in cells for v in values}
    for i in cells:
        for j in cells:
            model.add_constraint(model.sum(has[i, j, v] for v in values) == 1)
    x = [[model.sum(v * has[i, j, v] for v in values) for j in cells] for i in cells]

    # All rows and columns must be unique: each number once per row and per column.
    for v in values:
        for i in cells:
            model.add_constraint(model.sum(has[i, j, v] for j in cells) == 1)
        for j in cells:
            model.add_constraint(model.sum(has[i, j, v] for i in cells) == 1)

    # The primes that can divide a number in 1..n, and the exponent of each in each number.
    primes = sorted({p for v in values for p in prime_factors(v)})
    exponent = {(p, v): prime_factors(v).get(p, 0) for p in primes for v in values}

    for res, segment in cages:
        cage = [(r - 1, c - 1) for r, c in segment]
        if len(cage) == 2:
            # Two operands: the pair (a, b) must satisfy one of the six operations. The allowed
            # pairs are listed from the data; when a holds v, b holds a number that pairs with v,
            # and the other way round.
            (ai, aj), (bi, bj) = cage

            def pairs(a, b):
                return (a + b == res or a * b == res or a * res == b or b * res == a
                        or a - b == res or b - a == res)

            for v in values:
                model.add_constraint(has[ai, aj, v] <= model.sum(has[bi, bj, w] for w in values if pairs(v, w)))
                model.add_constraint(has[bi, bj, v] <= model.sum(has[ai, aj, w] for w in values if pairs(w, v)))
        else:
            # res is either the sum or the product of the cage. A product of numbers 1..n equals
            # res exactly when, for every prime up to n, the exponents of that prime in the
            # numbers add up to its exponent in res (and res has no larger prime factor). That
            # makes the product linear in the cell numbers. by_sum is 1 for the sum branch and 0
            # for the product branch.
            total = model.sum(x[i][j] for i, j in cage)
            res_factors = prime_factors(res) if res >= 1 else None
            product_possible = res_factors is not None and all(p in primes for p in res_factors)
            by_sum = model.binary_var(name=f"by_sum_{cage[0][0]}_{cage[0][1]}")
            model.add_indicator(by_sum, total == res, active_value=1)
            if product_possible:
                for p in primes:
                    count = model.sum(exponent[p, v] * has[i, j, v] for i, j in cage for v in values)
                    model.add_indicator(by_sum, count == res_factors.get(p, 0), active_value=0)
            else:
                model.add_constraint(by_sum == 1)

    return model, {"x": x}
