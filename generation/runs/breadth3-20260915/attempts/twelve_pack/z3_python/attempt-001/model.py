import z3


def build(instance):
    target, packs = instance["target"], instance["packs"]
    n = len(packs)
    ceiling = target * 2
    counts = [z3.Int(f"n_{i}") for i in range(n)]
    total = z3.Int("total")
    constraints = [c >= 0 for c in counts] + [c <= ceiling for c in counts]
    constraints += [total >= 0, total <= ceiling * n,
                    total == z3.Sum([counts[i] * packs[i] for i in range(n)]),
                    total >= target]
    return constraints, {"counts": counts}, ("minimize", total)
