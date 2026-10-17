# age_changing: my age m and my husband's age h (both non-negative integers).
# The four operations +2, /8, -3, *7 are each used once, in some order.
# Starting from my age and applying the operations in one order gives the husband's age h.
# Starting from his age and applying them in a different order gives my age m.
# Operation codes: 0 = +2, 1 = /8 (exact), 2 = -3, 3 = *7.
from cvc5.pythonic import Int, Ints, Distinct, Implies, Or, And


def apply_steps(start, codes, tag):
    # Chain of four steps: each step applies the operation whose code sits at that position.
    # Division by 8 is exact: the current value must be a multiple of 8.
    cons = []
    cur = start
    for k, code in enumerate(codes):
        nxt = Int(f"{tag}_{k}")
        cons.append(Implies(code == 0, nxt == cur + 2))
        cons.append(Implies(code == 1, cur == 8 * nxt))
        cons.append(Implies(code == 2, nxt == cur - 3))
        cons.append(Implies(code == 3, nxt == 7 * cur))
        cur = nxt
    return cons, cur


def build(instance):
    m, h = Int("m"), Int("h")
    fwd = Ints("f0 f1 f2 f3")  # order of the operations from my age to his
    bwd = Ints("g0 g1 g2 g3")  # order of the operations from his age to mine

    cons = [m >= 0, h >= 0]
    for codes in (fwd, bwd):
        for c in codes:
            cons.append(c >= 0)
            cons.append(c <= 3)
        cons.append(Distinct(list(codes)))

    # The two orders must differ in at least one position.
    cons.append(Or(*[fwd[k] != bwd[k] for k in range(4)]))

    # Starting from my age and applying the four operations in some order gives his age.
    c1, end1 = apply_steps(m, fwd, "a")
    cons.append(And(*c1, end1 == h))

    # Starting from his age and applying the four operations in a different order gives mine.
    c2, end2 = apply_steps(h, bwd, "b")
    cons.append(And(*c2, end2 == m))

    return cons, {"h": h, "m": m}
