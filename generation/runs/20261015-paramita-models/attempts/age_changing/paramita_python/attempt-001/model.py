"""Age changing: my age m and my husband's age h.

Four operations, each used once: +2, /8, -3, *7. Applying them in some order to my
age gives my husband's age. Applying them in a different order to his age gives mine.
Divisions must be exact and ages stay non-negative. Ages are whole years in 1..150
(the problem gives no bound; 150 is an assumption and is not a constraint of the puzzle).
"""
from itertools import permutations

from paramita.modelling import Bool, And, If

OPS = {
    "+2": lambda x: x + 2,
    "/8": lambda x: x // 8 if x % 8 == 0 else None,   # the division must come out whole
    "-3": lambda x: x - 3 if x >= 3 else None,        # no negative intermediate value
    "*7": lambda x: x * 7,
}


def apply_order(order, x):
    """Value after applying the operations of `order` to x, or None if a step is invalid."""
    for op in order:
        x = OPS[op](x)
        if x is None:
            return None
    return x


def build(instance):
    ages = range(1, 151)
    my = {v: Bool(f"my_age_{v}") for v in ages}
    hus = {v: Bool(f"husband_age_{v}") for v in ages}
    orders = list(permutations(OPS))
    fwd = {p: Bool(f"forward_order_{i}") for i, p in enumerate(orders)}
    bwd = {p: Bool(f"backward_order_{i}") for i, p in enumerate(orders)}

    cons = []

    # each age is a single whole number of years
    cons.append(sum(my.values()) == 1)
    cons.append(sum(hus.values()) == 1)

    # the four operations are applied in exactly one order to my age
    cons.append(sum(fwd.values()) == 1)
    # and in exactly one order to his age
    cons.append(sum(bwd.values()) == 1)

    for p in orders:
        # the second order must be a different order from the first
        cons.append(~(fwd[p] & bwd[p]))

        # my age, after the operations in order p, is his age
        for v in ages:
            w = apply_order(p, v)
            if w is None or w not in hus:
                cons.append(If(fwd[p], ~my[v]))
            else:
                cons.append(If(And(fwd[p], my[v]), hus[w]))

        # his age, after the operations in a different order, is my age
        for v in ages:
            w = apply_order(p, v)
            if w is None or w not in my:
                cons.append(If(bwd[p], ~hus[v]))
            else:
                cons.append(If(And(bwd[p], hus[v]), my[w]))

    h = sum(v * hus[v] for v in ages)   # husband's age
    m = sum(v * my[v] for v in ages)    # my age
    return cons, {"h": h, "m": m}
