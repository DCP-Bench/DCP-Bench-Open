"""Curious numbers (Dudeney, Amusements in Mathematics 114): 48 plus 1 is a square, and half
of 48 plus 1 is also a square. Find another number between 1 and 10000 with this property.

The model reports the number (peculiar).
"""
import math

import pulp


def build(instance):
    del instance  # the puzzle has no instance data; its bounds are below

    top = 10000  # every quantity lies in 1..10000, as in the reference
    known = 48   # the example from the puzzle, which the answer must differ from

    problem = pulp.LpProblem("cur_num", pulp.LpMinimize)  # satisfaction

    peculiar = pulp.LpVariable("peculiar", 1, top, cat="Integer")
    half = pulp.LpVariable("half", 1, top, cat="Integer")

    # Squares are not linear, so each square root is chosen from its range and its square
    # read off the same binaries. A root above isqrt(top) would square beyond the range.
    roots = range(1, math.isqrt(top) + 1)
    root_a = {r: pulp.LpVariable(f"root_a_{r}", cat="Binary") for r in roots}
    root_b = {r: pulp.LpVariable(f"root_b_{r}", cat="Binary") for r in roots}
    problem += pulp.lpSum(root_a.values()) == 1
    problem += pulp.lpSum(root_b.values()) == 1

    # if you add 1 to it, the result is a square number
    problem += peculiar + 1 == pulp.lpSum(r * r * var for r, var in root_a.items())

    # if you add 1 to its half, you also get a square number
    problem += peculiar == 2 * half
    problem += half + 1 == pulp.lpSum(r * r * var for r, var in root_b.items())

    # the number is not 48, which is already known: it lies below or above it
    above = pulp.LpVariable("above", cat="Binary")
    problem += peculiar <= known - 1 + top * above
    problem += peculiar >= known + 1 - top * (1 - above)

    return problem, {"peculiar": peculiar}
