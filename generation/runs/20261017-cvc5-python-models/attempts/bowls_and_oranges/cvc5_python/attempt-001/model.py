# Bowls and oranges: place m oranges in n bowls in a line at 1 meter intervals,
# at most one orange per bowl, so that there are no three oranges A, B, C with
# the distance between A and B equal to the distance between B and C.
# Output the bowls holding the oranges, in ascending order (x).
import cvc5.pythonic as cz


def _any_of(lits):
    return lits[0] if len(lits) == 1 else cz.Or(lits)


def build(instance):
    n = instance["n"]
    m = instance["m"]

    x = [cz.Int(f"x_{i}") for i in range(m)]
    occ = [cz.Bool(f"occ_{k}") for k in range(1, n + 1)]

    cons = []

    # Each orange is in a bowl numbered 1 to n. The bowls are listed in
    # ascending order, which also rules out two oranges in the same bowl.
    for xi in x:
        cons += [xi >= 1, xi <= n]
    for i in range(m - 1):
        cons.append(x[i] < x[i + 1])

    # A bowl is occupied exactly when some orange is placed in it.
    for k in range(1, n + 1):
        occ_k = occ[k - 1]
        cons.append(occ_k == _any_of([xi == k for xi in x]))

    # No three oranges A, B, C with the distance between A and B equal to the
    # distance between B and C: no three occupied bowls a < b < c in arithmetic
    # progression, b - a = c - b.
    for a in range(1, n + 1):
        for b in range(a + 1, n + 1):
            c = 2 * b - a
            if c > n:
                break
            cons.append(
                cz.Not(cz.And(occ[a - 1], occ[b - 1], occ[c - 1]))
            )

    s = cz.SolverFor("QF_LIA")
    s.add(*cons)
    return s, {"x": x}
