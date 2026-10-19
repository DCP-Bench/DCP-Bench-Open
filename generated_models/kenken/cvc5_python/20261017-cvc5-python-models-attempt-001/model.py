# KenKen: fill an n x n grid with the digits 1..n so that each row and each column
# contains every digit exactly once, and each cage's digits achieve its target
# under an operation that is part of the puzzle (to be determined).
import itertools

import cvc5.pythonic as cz


def any_of(terms):
    if not terms:
        return cz.BoolVal(False)
    if len(terms) == 1:
        return terms[0]
    return cz.Or(terms)


def all_of(terms):
    if len(terms) == 1:
        return terms[0]
    return cz.And(terms)


def cage_pair_ok(a, b, t):
    # Two-cell cage: sum, difference, product or exact quotient (larger over smaller).
    return (a + b == t) or (abs(a - b) == t) or (a * b == t) or (
        (a % b == 0 and a // b == t) or (b % a == 0 and b // a == t)
    )


def build(instance):
    n = instance["n"]
    digits = list(range(1, n + 1))
    x = [[cz.Int(f"x_{i}_{j}") for j in range(n)] for i in range(n)]

    constraints = []

    # Each cell takes a digit from 1 to n.
    # Each row contains exactly one of each digit.
    # Each column contains exactly one of each digit.
    for i in range(n):
        for j in range(n):
            constraints.append(x[i][j] >= 1)
            constraints.append(x[i][j] <= n)
    for i in range(n):
        constraints.append(cz.Distinct(x[i]))
    for j in range(n):
        constraints.append(cz.Distinct([x[i][j] for i in range(n)]))

    # Each bold-outlined group of cells is a cage containing digits which achieve
    # the specified result using the specified mathematical operation.
    # The operation is not given: it is one of addition, subtraction, multiplication
    # and division, with subtraction and division only for two-cell cages. Digits may
    # repeat within a cage.
    for target, cells in instance["problem"]:
        vals = [x[r - 1][c - 1] for r, c in cells]
        k = len(vals)

        if k == 1:
            constraints.append(vals[0] == target)
            continue

        if k == 2:
            # Union over the four operations of the allowed digit pairs, so the
            # solver picks the operation as part of the search.
            pairs = [(a, b) for a in digits for b in digits if cage_pair_ok(a, b, target)]
            constraints.append(
                any_of([all_of([vals[0] == a, vals[1] == b]) for a, b in pairs])
            )
            continue

        # Larger cages: sum or product (no subtraction or division).
        options = []
        options.append(cz.Sum(vals) == target)
        prod_tuples = []
        for tup in itertools.product(digits, repeat=k):
            p = 1
            for d in tup:
                p *= d
            if p == target:
                prod_tuples.append(tup)
        if prod_tuples:
            options.append(
                any_of([all_of([v == d for v, d in zip(vals, tup)]) for tup in prod_tuples])
            )
        constraints.append(any_of(options))

    return constraints, {"x": x}
