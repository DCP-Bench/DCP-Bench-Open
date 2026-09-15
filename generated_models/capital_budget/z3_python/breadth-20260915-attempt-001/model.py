import z3


def build(instance):
    budget, npv, cash_flow = instance["budget"], instance["npv"], instance["cash_flow"]
    n = len(npv)
    chosen = [z3.Bool(f"x_{i}") for i in range(n)]
    picked = [z3.If(chosen[i], 1, 0) for i in range(n)]
    total = z3.Int("z")
    constraints = [
        z3.Sum([cash_flow[i] * picked[i] for i in range(n)]) <= budget,
        total == z3.Sum([npv[i] * picked[i] for i in range(n)]),
        total >= 0, total <= sum(npv),
    ]
    return constraints, {"z": total, "x": chosen}, ("maximize", total)
