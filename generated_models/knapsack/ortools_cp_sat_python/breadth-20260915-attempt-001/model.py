from ortools.sat.python import cp_model


def build(instance):
    values, weights = instance["values"], instance["weights"]
    capacity = instance["capacity"]
    model = cp_model.CpModel()
    chosen = [model.new_bool_var(f"x_{i}") for i in range(len(values))]
    model.add(sum(w * chosen[i] for i, w in enumerate(weights)) <= capacity)
    model.maximize(sum(v * chosen[i] for i, v in enumerate(values)))
    return model, {"x": chosen}
