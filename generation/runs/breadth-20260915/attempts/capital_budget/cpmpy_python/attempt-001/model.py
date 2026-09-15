import cpmpy as cp


def build(instance):
    budget, npv, cash_flow = instance["budget"], instance["npv"], instance["cash_flow"]
    n = len(npv)
    chosen = cp.boolvar(shape=n, name="x")
    total = cp.intvar(0, sum(npv), name="z")
    model = cp.Model(
        cp.sum([cash_flow[i] * chosen[i] for i in range(n)]) <= budget,
        total == cp.sum([npv[i] * chosen[i] for i in range(n)]),
    )
    model.maximize(total)
    return model, {"z": total, "x": [chosen[i] for i in range(n)]}
