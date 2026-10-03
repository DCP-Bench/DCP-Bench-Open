"""Curious set of integers (Martin Gardner): in the set 1, 3, 8, 120 the product of any two
members is one less than a perfect square. Find a further number, at least 0, that can join
the set without destroying this property.

The model reports the new number.
"""
import math

import pulp


def build(instance):
    n = instance["n"]              # size of the extended set
    max_val = instance["max_val"]  # bound on every number and every square root

    known = [1, 3, 8, 120]  # the set from the puzzle statement
    if n != len(known) + 1:
        # The products of two unknown numbers are not linear; the reference's case adds
        # exactly one number, which keeps every product linear in it.
        raise ValueError("this model adds exactly one number to the known set")

    problem = pulp.LpProblem("curious_set_of_integers", pulp.LpMinimize)  # satisfaction

    number = pulp.LpVariable("number", 0, max_val, cat="Integer")

    # the members are all different: the new number is none of the known ones
    for k in known:
        side = pulp.LpVariable(f"above_{k}", cat="Binary")
        problem += number <= k - 1 + (max_val + 1) * side
        problem += number >= k + 1 - (max_val + 1) * (1 - side)

    # the product of any two known members is one less than a square of a root in
    # 0..max_val (these are constants; a pair that fails makes the problem infeasible)
    for a in known:
        for b in known:
            if a != b:
                r = math.isqrt(a * b + 1)
                if r * r != a * b + 1 or r > max_val:
                    problem += number <= -1

    # the product of the new number with each known member is one less than a perfect
    # square: number * k + 1 == root * root. The square is not linear, so the root is
    # chosen from its range 0..max_val, cut where its square exceeds k * max_val + 1.
    for k in known:
        roots = range(0, min(max_val, math.isqrt(k * max_val + 1)) + 1)
        root = {r: pulp.LpVariable(f"root_{k}_{r}", cat="Binary") for r in roots}
        problem += pulp.lpSum(root.values()) == 1
        problem += k * number + 1 == pulp.lpSum(r * r * var for r, var in root.items())

    return problem, {"number": number}
