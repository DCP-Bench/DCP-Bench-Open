# Twelve-pack problem: items are sold in packs of given sizes. Find how many packs of
# each size to buy so that the total number of items is at least the target and as close
# to it as possible.
from pychoco.model import Model


def build(instance):
    target = instance["target"]  # number of items wanted
    packs = instance["packs"]  # pack sizes
    n = len(packs)
    max_val = target * 2  # the reference's arbitrary limit on the number of packs of one size

    model = Model()

    # counts[i] = number of packs of size packs[i] bought
    counts = [model.intvar(0, max_val, name=f"counts_{i}") for i in range(n)]
    # total = total number of items bought (same range as the reference's variable)
    total = model.intvar(0, max_val * n, name="total", bounded_domain=True)

    # the total is the sum over pack sizes of (packs bought * pack size)
    model.scalar(counts, packs, "=", total).post()

    # at least the target number of items must be bought
    model.arithm(total, ">=", target).post()

    # buy as few items as possible, i.e. get as close to the target as possible
    return model, {"counts": counts}, ("minimize", total)
