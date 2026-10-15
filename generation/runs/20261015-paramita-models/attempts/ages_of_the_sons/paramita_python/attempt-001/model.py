"""Ages of the three sons (A1 >= A2 >= A3, oldest first).

Puzzle facts: the product of the ages is 36; the sum equals the number of windows, which
is not given; the mathematician needs more information after the product and again after
the sum; after learning that the oldest son is unique (blue eyes), he knows the ages.
"""
from paramita.modelling import Bool, If, Or

PRODUCT = 36


def build(instance):
    # Candidate triples: sorted factorisations of the product into three positive factors.
    divisors = [d for d in range(1, PRODUCT + 1) if PRODUCT % d == 0]
    cands = [(x, y, z) for x in divisors for y in divisors for z in divisors
             if x >= y >= z and x * y * z == PRODUCT]
    total = {i: c[0] + c[1] + c[2] for i, c in enumerate(cands)}
    t = {i: Bool(f"sons_are_candidate_{i}") for i in range(len(cands))}
    v = {i: Bool(f"other_candidate_{i}") for i in range(len(cands))}

    cons = []

    # the real ages are exactly one candidate triple
    cons.append(sum(t.values()) == 1)

    # The sum of their ages equals the number of windows. The mathematician still needs
    # more information, so another candidate triple with the same sum must exist.
    cons.append(sum(v.values()) == 1)
    for i in range(len(cands)):
        # the other candidate is a different triple
        cons.append(~(t[i] & v[i]))
        # the other candidate has the same sum as the real ages
        for j in range(len(cands)):
            if total[i] != total[j]:
                cons.append(If(t[i], ~v[j]))

    # The oldest son has blue eyes: the oldest is unique, so A1 > A2 for the real ages.
    for i, (x, y, z) in enumerate(cands):
        if x == y:
            cons.append(~t[i])

    # The mathematician got it: among triples with a unique oldest son and the same sum,
    # the real ages are the only one.
    for j, (x, y, z) in enumerate(cands):
        if x == y:
            continue
        same_sum = [t[k] for k in range(len(cands)) if total[k] == total[j]]
        cons.append(If(Or(same_sum), t[j]))

    a1 = sum(c[0] * t[i] for i, c in enumerate(cands))
    a2 = sum(c[1] * t[i] for i, c in enumerate(cands))
    a3 = sum(c[2] * t[i] for i, c in enumerate(cands))
    return cons, {"A1": a1, "A2": a2, "A3": a3}
