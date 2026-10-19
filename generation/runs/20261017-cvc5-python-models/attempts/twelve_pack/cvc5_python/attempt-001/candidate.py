# Twelve-pack problem: given a target number of items and pack sizes,
# find the closest combination of packs that meets or exceeds the target.
# Output: counts, the number of packs used of each size.

import cvc5.pythonic as cz


def build(instance):
    target = instance["target"]
    packs = instance["packs"]
    n = len(packs)

    counts = cz.Ints(" ".join(f"c{i}" for i in range(n)))
    if n == 1:
        counts = [counts]

    # packs of different sizes: the number of packs of each size is a non-negative integer.
    bounds = []
    for c in counts:
        bounds.append(c >= 0)

    # implied bound on the number of packs of each size: an optimal combination
    # never has a pack whose removal still meets the target, so each count is
    # at most target // p + 1. The optimal solutions are kept.
    for c, p in zip(counts, packs):
        bounds.append(c <= target // p + 1)

    # a combination of packs that meets or exceeds the target
    total = cz.Sum([c * p for c, p in zip(counts, packs)])
    meets_target = [total >= target]

    # the closest combination: the total number of items packed is as small as possible
    return bounds + meets_target, {"counts": counts}, ("minimize", total)
