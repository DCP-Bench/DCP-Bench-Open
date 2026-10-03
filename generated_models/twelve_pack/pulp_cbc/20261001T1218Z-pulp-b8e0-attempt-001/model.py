"""Twelve pack: items are sold in packs of given sizes. Buy packs so that the number of items
is at least the target and as close to it as possible (the fewest items that reach the target).

The model reports how many packs of each size are bought.
"""
import pulp


def build(instance):
    target = instance["target"]  # number of items wanted
    packs = instance["packs"]  # pack sizes
    n = len(packs)
    max_count = target * 2  # most packs of one size considered (the same limit as the reference)

    problem = pulp.LpProblem("twelve_pack", pulp.LpMinimize)

    # counts[i] = number of packs of size packs[i] that are bought
    counts = [pulp.LpVariable(f"counts_{i}", 0, max_count, cat="Integer") for i in range(n)]

    # total = number of items bought
    total = pulp.LpVariable("total", 0, max_count * n, cat="Integer")
    problem += total == pulp.lpSum(packs[i] * counts[i] for i in range(n))

    # the items bought reach the target
    problem += total >= target

    # minimise the number of items bought
    problem += total

    return problem, {"counts": counts}
