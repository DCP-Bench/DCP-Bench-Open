# KenKen: fill an n x n grid with the digits 1..n so that every row and column holds each digit
# once, and every cage (a group of cells) reaches its target. A cage of two cells reaches it
# by sum, product, difference or exact quotient of its two digits; a cage of any other size by
# the sum or the product of its digits. Digits may repeat inside a cage.
from itertools import product

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def cage_holds(digits, target):
    """Does a cage with these digits (in the order of its cells) reach the target?"""
    if len(digits) == 2:
        a, b = digits
        return (a + b == target or a * b == target or a * target == b
                or b * target == a or a - b == target or b - a == target)
    total, multiplied = 0, 1
    for digit in digits:
        total += digit
        multiplied *= digit
    return total == target or multiplied == target


def build(instance):
    n = instance["n"]
    cages = instance["problem"]  # [target, [[row, column], ...]] per cage, cells numbered from 1

    pool = IDPool()
    # x[r][c] = the digit in row r, column c
    x = [[Integer(f"x_{r}_{c}", 1, n, vpool=pool) for c in range(n)] for r in range(n)]
    engine = IntegerEngine(vars=[cell for row in x for cell in row], vpool=pool)

    # every row and every column holds different digits
    for i in range(n):
        engine.add_alldifferent(x[i])
        engine.add_alldifferent([x[r][i] for r in range(n)])
    cnf = engine.clausify()

    # Each cage: the digits of its cells must be one of the digit combinations that reach the target.
    # The combinations are listed (at most n^size candidates, tested with the rule above) and
    # chosen[k] is true when the k-th listed combination is the one in the grid. A table of
    # allowed combinations is used because a sum-or-product (or one of four operations) cannot
    # be stated as a single linear constraint.
    for index, (target, cells) in enumerate(cages):
        cage = [x[r - 1][c - 1] for r, c in cells]
        allowed = [digits for digits in product(range(1, n + 1), repeat=len(cage))
                   if cage_holds(digits, target)]
        chosen = [pool.id(("cage", index, k)) for k in range(len(allowed))]
        cnf.append(chosen)  # some allowed combination is in the grid (empty: the cage is impossible)
        for selector, digits in zip(chosen, allowed):
            for cell, digit in zip(cage, digits):
                cnf.append([-selector, cell.equals(digit)])

    return cnf, {"x": x}
