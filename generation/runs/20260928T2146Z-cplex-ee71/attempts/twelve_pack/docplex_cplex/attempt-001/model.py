"""Twelve pack: buy packs of the given sizes to get at least the target number of items, as few over it as possible."""
from docplex.mp.model import Model


def build(instance):
    packs, target = instance["packs"], instance["target"]
    # The reference model caps each pack count at twice the target, and the
    # total number of items at that cap times the number of pack sizes.
    max_count = 2 * target

    model = Model("twelve_pack")

    # counts[i] is how many packs of size i are bought.
    counts = model.integer_var_list(len(packs), 0, max_count, name="counts")

    # total is the number of items bought, which meets or exceeds the target.
    total = model.integer_var(0, max_count * len(packs), name="total")
    model.add_constraint(total == model.dot(counts, packs), ctname="items")
    model.add_constraint(total >= target, ctname="enough")

    # Get as close to the target as possible, which means buying the fewest items.
    model.minimize(total)

    return model, {"counts": counts}
