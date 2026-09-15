from ortools.sat.python import cp_model


def build(instance):
    target, packs = instance["target"], instance["packs"]
    n = len(packs)
    ceiling = target * 2
    model = cp_model.CpModel()
    counts = [model.new_int_var(0, ceiling, f"n_{i}") for i in range(n)]
    total = model.new_int_var(0, ceiling * n, "total")
    model.add(total == sum(counts[i] * packs[i] for i in range(n)))
    model.add(total >= target)
    model.minimize(total)
    return model, {"counts": counts}
