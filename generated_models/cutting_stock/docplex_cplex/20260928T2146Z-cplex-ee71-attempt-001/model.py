"""Cutting stock: choose how often to cut each pattern so every order is met with as few raw rolls as possible."""
from docplex.mp.model import Model


def build(instance):
    pieces = instance["num_rolls_width"]  # pieces[p][w]: pieces of width w one cut of pattern p yields
    orders = instance["orders"]
    patterns = range(instance["num_patterns"])
    widths = range(len(instance["widths"]))

    model = Model("cutting_stock")

    # patterns_used[p] is how many raw rolls are cut with pattern p. The bound of
    # 100 is the domain the problem's reference model declares.
    patterns_used = model.integer_var_list(instance["num_patterns"], 0, 100, name="patterns_used")

    # For each width, the pieces cut meet the number ordered.
    for w in widths:
        model.add_constraint(model.sum(pieces[p][w] * patterns_used[p] for p in patterns) >= orders[w],
                             ctname=f"order_{w}")

    # Minimise the number of raw rolls cut.
    min_rolls_cut = model.sum(patterns_used)
    model.minimize(min_rolls_cut)

    return model, {"patterns_used": patterns_used, "min_rolls_cut": min_rolls_cut}
