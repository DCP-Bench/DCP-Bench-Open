from pyscipopt import Model, quicksum

# Cutting stock: cut raw rolls into pieces of each width so that every
# width's order is met, using as few raw rolls as possible.
def build(instance):
    roll_width = instance["roll_width"]
    widths = instance["widths"]
    orders = instance["orders"]
    num_patterns = instance["num_patterns"]
    # num_rolls_width[p][w]: number of pieces of width w that pattern p cuts
    num_rolls_width = instance["num_rolls_width"]
    num_widths = len(widths)

    m = Model()

    # patterns_used[p]: how many raw rolls are cut with pattern p.
    # Each pattern can be used at most max(orders) times: using it more is
    # never needed to meet an order, so the bound does not cut off optima.
    max_order = max(orders)
    x = [m.addVar(name=f"x_{p}", vtype="I", lb=0, ub=max_order) for p in range(num_patterns)]

    # the total number of pieces cut of each width meets its order
    for w in range(num_widths):
        # the pieces of this width cut from all rolls meet its order
        m.addCons(
            quicksum(num_rolls_width[p][w] * x[p] for p in range(num_patterns)) >= orders[w]
        )

    # the objective is the total number of raw rolls cut
    m.setObjective(quicksum(x), "minimize")

    outputs = {
        "min_rolls_cut": quicksum(x),
        "patterns_used": x,
    }
    return m, outputs
