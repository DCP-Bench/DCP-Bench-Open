from ortools.sat.python import cp_model

# The reference's own domain for x.
LOW, HIGH = 0, 7


def build(instance):
    n, wanted, values = instance["n"], instance["m"], instance["v"]
    model = cp_model.CpModel()
    x = [model.new_int_var(LOW, HIGH, f"x_{i}") for i in range(n)]
    matches = []
    for i in range(n):
        for value in values:
            hit = model.new_bool_var(f"hit_{i}_{value}")
            model.add(x[i] == value).only_enforce_if(hit)
            model.add(x[i] != value).only_enforce_if(~hit)
            matches.append(hit)
    model.add(sum(matches) == wanted)
    return model, {"x": x}
