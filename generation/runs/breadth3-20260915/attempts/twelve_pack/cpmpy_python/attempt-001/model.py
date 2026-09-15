import cpmpy as cp


def build(instance):
    target, packs = instance["target"], instance["packs"]
    n = len(packs)
    # The reference's own arbitrary ceiling on a pack count.
    ceiling = target * 2
    counts = cp.intvar(0, ceiling, shape=n, name="counts")
    total = cp.intvar(0, ceiling * n, name="total")
    model = cp.Model(total == cp.sum([counts[i] * packs[i] for i in range(n)]), total >= target)
    model.minimize(total)
    return model, {"counts": [counts[i] for i in range(n)]}
