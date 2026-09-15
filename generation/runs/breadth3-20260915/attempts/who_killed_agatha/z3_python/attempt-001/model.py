import z3


def build(instance):
    # The reference numbers the residents 0 Agatha, 1 the butler, 2 Charles.
    n = len(instance["names"])
    agatha, butler, charles, victim = 0, 1, 2, 0
    killer = z3.Int("killer")
    hates = [[z3.Bool(f"hates_{i}_{j}") for j in range(n)] for i in range(n)]
    richer = [[z3.Bool(f"richer_{i}_{j}") for j in range(n)] for i in range(n)]
    constraints = [killer >= 0, killer <= n - 1]
    for i in range(n):
        # A killer always hates, and is no richer than, his victim.
        constraints.append(z3.Implies(killer == i, hates[i][victim]))
        constraints.append(z3.Implies(killer == i, z3.Not(richer[i][victim])))
        constraints.append(z3.Not(richer[i][i]))
        for j in range(i + 1, n):
            constraints.append(richer[i][j] == z3.Not(richer[j][i]))
        # Charles hates nobody that Agatha hates.
        constraints.append(z3.Implies(hates[agatha][i], z3.Not(hates[charles][i])))
        # The butler hates everyone not richer than Agatha, and everyone Agatha hates.
        constraints.append(z3.Implies(z3.Not(richer[i][agatha]), hates[butler][i]))
        constraints.append(z3.Implies(hates[agatha][i], hates[butler][i]))
        # Nobody hates everyone.
        constraints.append(z3.Sum([z3.If(hates[i][j], 1, 0) for j in range(n)]) <= 2)
    # Agatha hates everybody except the butler.
    constraints += [hates[agatha][agatha], hates[agatha][charles], z3.Not(hates[agatha][butler])]
    return constraints, {"killer": killer}
