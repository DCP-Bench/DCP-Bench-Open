# Who killed Aunt Agatha? (Dreadsbury Mansion puzzle)
# Three people live in Dreadsbury Mansion: Agatha (0), the butler (1), Charles (2).
# Output: the 0-based index of the killer.
import cvc5.pythonic as cz


def build(instance):
    n = len(instance["names"])
    agatha, butler, charles = 0, 1, 2
    people = [agatha, butler, charles]

    hates = [[cz.Bool(f"hates_{i}_{j}") for j in range(n)] for i in range(n)]
    richer = [[cz.Bool(f"richer_{i}_{j}") for j in range(n)] for i in range(n)]
    killer = cz.Int("killer")

    cons = [killer >= 0, killer <= 2]

    # Richer is a strict relation: irreflexive and asymmetric.
    for i in range(n):
        cons.append(cz.Not(richer[i][i]))
        for j in range(n):
            if i != j:
                cons.append(cz.Implies(richer[i][j], cz.Not(richer[j][i])))

    # A killer always hates his victim, and is no richer than his victim.
    # The victim is Agatha.
    for p in people:
        cons.append(cz.Implies(killer == p, cz.And(hates[p][agatha], cz.Not(richer[p][agatha]))))

    # Agatha hates everybody except the butler.
    cons.append(hates[agatha][agatha])
    cons.append(cz.Not(hates[agatha][butler]))
    cons.append(hates[agatha][charles])

    # The butler hates everyone not richer than Aunt Agatha.
    for j in range(n):
        cons.append(cz.Implies(cz.Not(richer[j][agatha]), hates[butler][j]))

    # The butler hates everyone whom Agatha hates.
    for j in range(n):
        cons.append(cz.Implies(hates[agatha][j], hates[butler][j]))

    # Charles hates no one that Agatha hates.
    for j in range(n):
        cons.append(cz.Implies(hates[agatha][j], cz.Not(hates[charles][j])))

    # No one hates everyone.
    for i in range(n):
        cons.append(cz.Or([cz.Not(hates[i][j]) for j in range(n)]))

    return cons, {"killer": killer}
