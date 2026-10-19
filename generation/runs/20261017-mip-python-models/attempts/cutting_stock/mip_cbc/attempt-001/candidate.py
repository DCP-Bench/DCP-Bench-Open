# Cutting stock: raw rolls of width RollWidth are cut into pieces of the given widths.
# There are NumPatterns cutting patterns; pattern p gives num_rolls_width[p][i] pieces of width i.
# Choose how many times each pattern is used, minimising the total number of raw rolls cut.
import mip


def build(instance):
    num_patterns = instance["num_patterns"]
    counts = instance["num_rolls_width"]
    orders = instance["orders"]
    num_widths = len(orders)
    max_order = max(orders)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    used = [
        model.add_var(name=f"used_{p}", lb=0, ub=max_order, var_type=mip.INTEGER)
        for p in range(num_patterns)
    ]
    total = model.add_var(
        name="total", lb=0, ub=num_patterns * max_order, var_type=mip.INTEGER
    )

    # the total number of raw rolls cut is the sum of the number of times each pattern is used
    model.add_constr(total == mip.xsum(used))

    # for each width, the total number of rolls cut meets the total Orders
    for i in range(num_widths):
        model.add_constr(
            mip.xsum(counts[p][i] * used[p] for p in range(num_patterns)) >= orders[i]
        )

    model.objective = total
    return model, {"min_rolls_cut": total, "patterns_used": used}
