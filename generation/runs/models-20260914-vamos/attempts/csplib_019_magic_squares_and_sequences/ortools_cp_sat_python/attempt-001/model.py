from ortools.sat.python import cp_model


def build(instance):
    n = instance["n"]
    model = cp_model.CpModel()
    x = [model.new_int_var(0, n - 1, f"x_{j}") for j in range(n)]
    # is_value[j][i] is true exactly when x[j] takes the value i.
    is_value = [[model.new_bool_var(f"is_{j}_{i}") for i in range(n)] for j in range(n)]
    for j in range(n):
        for i in range(n):
            model.add(x[j] == i).only_enforce_if(is_value[j][i])
            model.add(x[j] != i).only_enforce_if(~is_value[j][i])
        model.add_exactly_one(is_value[j])
    for i in range(n):
        model.add(x[i] == sum(is_value[j][i] for j in range(n)))
    return model, {"x": x}
