from ortools.sat.python import cp_model


def build(instance):
    orders, pattern_yield = instance["orders"], instance["num_rolls_width"]
    patterns, widths = instance["num_patterns"], len(instance["widths"])
    model = cp_model.CpModel()
    used = [model.new_int_var(0, 100, f"p_{j}") for j in range(patterns)]
    for i in range(widths):
        model.add(sum(pattern_yield[j][i] * used[j] for j in range(patterns)) >= orders[i])
    rolls = sum(used)
    model.minimize(rolls)
    return model, {"patterns_used": used, "min_rolls_cut": rolls}
