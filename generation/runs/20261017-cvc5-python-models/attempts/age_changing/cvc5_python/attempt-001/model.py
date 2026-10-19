# age_changing: my age m and my husband's age h (both non-negative integers).
# Four operations, each used once, in some order: +2, /8, -3, *7.
# Starting from my age and applying the operations in one order gives the husband's age h.
# Starting from his age and applying them in a different order gives my age m.
import itertools

from cvc5.pythonic import Int, Or, And

OPS = ["add2", "div8", "sub3", "mul7"]


def chain(start, order, tag):
    # Applies the operations in the given order to `start`. Division by 8 is exact:
    # the current value must be a multiple of 8.
    cons = []
    cur = start
    for k, op in enumerate(order):
        nxt = Int(f"{tag}_{k}")
        if op == "add2":
            cons.append(nxt == cur + 2)
        elif op == "sub3":
            cons.append(nxt == cur - 3)
        elif op == "mul7":
            cons.append(nxt == cur * 7)
        else:  # div8
            cons.append(cur == 8 * nxt)
        cur = nxt
    return cons, cur


def build(instance):
    m, h = Int("m"), Int("h")

    # Ages are non-negative.
    base = [m >= 0, h >= 0]

    # Starting from my age and applying the four operations in some order gives h.
    # Starting from his age and applying them in a different order gives m.
    # The two orders must differ.
    options = []
    for p_idx, p in enumerate(itertools.permutations(OPS)):
        for q_idx, q in enumerate(itertools.permutations(OPS)):
            if p == q:
                continue
            cons1, end1 = chain(m, p, f"a{p_idx}")
            cons2, end2 = chain(h, q, f"b{q_idx}")
            options.append(And(*cons1, end1 == h, *cons2, end2 == m))

    return base + [Or(*options)], {"h": h, "m": m}
