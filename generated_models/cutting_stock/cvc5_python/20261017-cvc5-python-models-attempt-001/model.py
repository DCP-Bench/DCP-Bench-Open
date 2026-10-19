# Cutting stock problem: raw rolls of a fixed width are cut into pieces of several widths,
# each cutting pattern giving a number of pieces of each width. Decide how many rolls to cut
# with each pattern so that the total number of rolls cut is minimal.
import cvc5.pythonic as cz


def build(instance):
    num_patterns = instance["num_patterns"]
    widths = instance["widths"]
    orders = instance["orders"]
    rolls = instance["num_rolls_width"]
    num_widths = len(widths)

    used = [cz.Int(f"used_{p}") for p in range(num_patterns)]

    # Number of rolls cut with each pattern is a non-negative integer. Each pattern is used
    # at most as often as the total of all orders, which covers every optimal solution.
    max_use = sum(orders)
    domain = []
    for u in used:
        domain.append(u >= 0)
        domain.append(u <= max_use)

    # For each width, the total number of rolls cut meets the total Orders for that width.
    demand = []
    for w in range(num_widths):
        cut = cz.Sum([rolls[p][w] * used[p] for p in range(num_patterns)])
        demand.append(cut >= orders[w])

    # Minimise the total number of raw rolls cut.
    total = cz.Sum(used)

    constraints = domain + demand
    outputs = {"min_rolls_cut": total, "patterns_used": used}
    return constraints, outputs, ("minimize", total)
