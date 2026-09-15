import z3


def build(instance):
    orders, pattern_yield = instance["orders"], instance["num_rolls_width"]
    patterns, widths = instance["num_patterns"], len(instance["widths"])
    used = [z3.Int(f"p_{j}") for j in range(patterns)]
    constraints = [u >= 0 for u in used] + [u <= 100 for u in used]
    for i in range(widths):
        constraints.append(z3.Sum([pattern_yield[j][i] * used[j] for j in range(patterns)]) >= orders[i])
    rolls = z3.Sum(used)
    return constraints, {"patterns_used": used, "min_rolls_cut": rolls}, ("minimize", rolls)
