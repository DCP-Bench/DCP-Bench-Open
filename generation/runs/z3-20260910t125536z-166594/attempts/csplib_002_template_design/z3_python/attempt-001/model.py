import z3


def build(instance):
    n_slots = instance["n_slots"]
    n_templates = instance["n_templates"]
    n_var = instance["n_var"]
    demand = instance["demand"]
    upper = max(demand)

    production = [z3.Int(f"production_{t}") for t in range(n_templates)]
    layout = [[z3.Int(f"layout_{t}_{v}") for v in range(n_var)] for t in range(n_templates)]

    constraints = []
    for sheets in production:
        constraints.append(z3.And(sheets >= 1, sheets <= upper))
    for row in layout:
        for slots in row:
            constraints.append(z3.And(slots >= 0, slots <= n_var))
        # Every slot on a template is populated.
        constraints.append(z3.Sum(row) == n_slots)
    # Meet demand per variation. This is a product of two decision variables,
    # so it is nonlinear integer arithmetic for Z3.
    for variation in range(n_var):
        printed = [production[t] * layout[t][variation] for t in range(n_templates)]
        constraints.append(z3.Sum(printed) >= demand[variation])

    return constraints, {"production": production, "layout": layout}, ("minimize", z3.Sum(production))
