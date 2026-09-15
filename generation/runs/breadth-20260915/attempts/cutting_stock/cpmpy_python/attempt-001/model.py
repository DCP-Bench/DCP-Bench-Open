import cpmpy as cp


def build(instance):
    orders, pattern_yield = instance["orders"], instance["num_rolls_width"]
    patterns, widths = instance["num_patterns"], len(instance["widths"])
    used = cp.intvar(0, 100, shape=patterns, name="patterns_used")
    model = cp.Model()
    for i in range(widths):
        model += cp.sum([pattern_yield[j][i] * used[j] for j in range(patterns)]) >= orders[i]
    rolls = cp.sum([used[j] for j in range(patterns)])
    model.minimize(rolls)
    return model, {"patterns_used": [used[j] for j in range(patterns)], "min_rolls_cut": rolls}
