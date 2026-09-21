# Fewest items from whole packs that still meet the target.
from dcp_maxsat import MaxSat


def build(instance):
    packs = instance["packs"]
    target = instance["target"]
    n = len(packs)

    sat = MaxSat()
    # No pack is ever needed more often than the target divided by its size,
    # plus one to allow overshooting the target.
    counts = [sat.int(0, target // packs[i] + 1) for i in range(n)]
    ceiling = sum((target // packs[i] + 1) * packs[i] for i in range(n))
    total = sat.int(0, ceiling)
    sat.link_sum(list(zip(packs, counts)), total)
    sat.linear_ge([(1, total)], target)
    return sat, {"counts": counts}, ("minimize", total)
