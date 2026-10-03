"""Balanced incomplete block design (BIBD): arrange v objects in b blocks so that every
block holds exactly k objects, every object lies in exactly r blocks, and every two
distinct objects lie together in exactly lambda blocks.

The model reports the v x b incidence matrix (1 if the object is in the block).
"""
import itertools

import pulp


def build(instance):
    v = instance["v"]  # number of objects
    b = instance["b"]  # number of blocks
    r = instance["r"]  # blocks each object occurs in
    k = instance["k"]  # objects each block contains
    lam = instance["l"]  # blocks in which each pair of objects occurs together

    problem = pulp.LpProblem("bibd", pulp.LpMinimize)  # satisfaction: no objective

    # matrix[i][c] = 1 if object i is in block c
    matrix = [[pulp.LpVariable(f"matrix_{i}_{c}", cat="Binary") for c in range(b)]
              for i in range(v)]

    # every object occurs in exactly r blocks
    for i in range(v):
        problem += pulp.lpSum(matrix[i]) == r
    # every block contains exactly k objects
    for c in range(b):
        problem += pulp.lpSum(matrix[i][c] for i in range(v)) == k

    # every pair of distinct objects occurs together in exactly lambda blocks.
    # both[(i, j)][c] = matrix[i][c] AND matrix[j][c] (the product, which is not linear).
    both = {}
    for i, j in itertools.combinations(range(v), 2):
        both[(i, j)] = [pulp.LpVariable(f"both_{i}_{j}_{c}", cat="Binary") for c in range(b)]
        for c in range(b):
            problem += both[(i, j)][c] <= matrix[i][c]
            problem += both[(i, j)][c] <= matrix[j][c]
            problem += both[(i, j)][c] >= matrix[i][c] + matrix[j][c] - 1
        problem += pulp.lpSum(both[(i, j)]) == lam

    # Implied constraints that tighten the LP relaxation: a block with k objects holds
    # k(k-1)/2 pairs, and object i in a block is paired with the k-1 others of that block.
    for c in range(b):
        problem += pulp.lpSum(both[pair][c] for pair in both) == k * (k - 1) // 2
        for i in range(v):
            problem += pulp.lpSum(
                both[(min(i, j), max(i, j))][c] for j in range(v) if j != i
            ) == (k - 1) * matrix[i][c]

    return problem, {"matrix": matrix}
