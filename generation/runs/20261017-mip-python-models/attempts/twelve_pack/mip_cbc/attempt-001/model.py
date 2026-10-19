# Twelve-pack problem: given a target number of items and a set of pack sizes,
# choose how many packs of each size to use so that the total number of items
# meets or exceeds the target as closely as possible (minimise the total).
import mip


def build(instance):
    packs = instance["packs"]
    target = instance["target"]
    n = len(packs)
    max_pack = max(packs)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Any optimal solution has less than target + max_pack items in total: otherwise
    # one pack could be removed and the target would still be met. This bounds each count.
    counts = [
        model.add_var(f"counts_{i}", lb=0, ub=(target + max_pack) // packs[i], var_type=mip.INTEGER)
        for i in range(n)
    ]

    # The total number of items must meet or exceed the target.
    model += mip.xsum(packs[i] * counts[i] for i in range(n)) >= target

    # Minimise the total number of items, which is the same as minimising the excess over the target.
    model.objective = mip.xsum(packs[i] * counts[i] for i in range(n))

    return model, {"counts": counts}
