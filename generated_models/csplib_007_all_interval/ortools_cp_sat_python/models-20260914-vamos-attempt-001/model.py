from ortools.sat.python import cp_model


def build(instance):
    n = instance["n"]
    model = cp_model.CpModel()
    x = [model.new_int_var(0, n - 1, f"x_{i}") for i in range(n)]
    diffs = [model.new_int_var(1, n - 1, f"diffs_{i}") for i in range(n - 1)]
    model.add_all_different(x)
    model.add_all_different(diffs)
    for i in range(n - 1):
        model.add_abs_equality(diffs[i], x[i + 1] - x[i])
    return model, {"x": x, "diffs": diffs}
