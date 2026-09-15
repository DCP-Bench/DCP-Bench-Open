import cpmpy as cp


def build(instance):
    # The reference numbers the residents 0 Agatha, 1 the butler, 2 Charles.
    n = len(instance["names"])
    agatha, butler, charles, victim = 0, 1, 2, 0
    killer = cp.intvar(0, n - 1, name="killer")
    hates = cp.boolvar(shape=(n, n), name="hates")
    richer = cp.boolvar(shape=(n, n), name="richer")
    model = cp.Model(
        # A killer always hates, and is no richer than, his victim.
        hates[killer, victim] == 1,
        richer[killer, victim] == 0,
        # Nobody is richer than himself, and richness is antisymmetric.
        [~richer[i, i] for i in range(n)],
        [richer[i, j] == (~richer[j, i]) for i in range(n) for j in range(i + 1, n)],
        # Charles hates nobody that Agatha hates.
        [hates[agatha, i].implies(~hates[charles, i]) for i in range(n)],
        # Agatha hates everybody except the butler.
        hates[agatha, agatha] == 1, hates[agatha, charles] == 1, hates[agatha, butler] == 0,
        # The butler hates everyone not richer than Agatha, and everyone Agatha hates.
        [(~richer[i, agatha]).implies(hates[butler, i]) for i in range(n)],
        [hates[agatha, i].implies(hates[butler, i]) for i in range(n)],
        # Nobody hates everyone.
        [cp.sum([hates[i, j] for j in range(n)]) <= 2 for i in range(n)],
    )
    return model, {"killer": killer}
