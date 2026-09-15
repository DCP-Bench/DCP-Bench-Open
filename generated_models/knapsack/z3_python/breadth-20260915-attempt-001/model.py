import z3


def build(instance):
    values, weights = instance["values"], instance["weights"]
    capacity = instance["capacity"]
    chosen = [z3.Bool(f"x_{i}") for i in range(len(values))]
    picked = [z3.If(chosen[i], 1, 0) for i in range(len(values))]
    constraints = [z3.Sum([w * picked[i] for i, w in enumerate(weights)]) <= capacity]
    objective = z3.Sum([v * picked[i] for i, v in enumerate(values)])
    return constraints, {"x": chosen}, ("maximize", objective)
