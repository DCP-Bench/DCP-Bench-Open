"""Initials queue: ten people queue for a lecture, each with initials that are an
alphabetically ordered pair of distinct letters from A..E, no two with the same initials,
and no one sharing a letter with the person in front. BE is first, CD second and BD last.

The model reports the queue as pairs of letters 0..4 (A..E), front first.
"""
from itertools import combinations

import pulp


def build(instance):
    del instance  # the puzzle has no instance data

    n = 10
    A, B, C, D, E = range(5)
    # 1. initials are alphabetically ordered pairs of distinct letters
    pairs = list(combinations(range(5), 2))

    problem = pulp.LpProblem("initials_queue", pulp.LpMinimize)  # satisfaction

    # has[i][p] = 1 if person i in the queue has the initials pairs[p]
    has = [[pulp.LpVariable(f"has_{i}_{p[0]}{p[1]}", cat="Binary") for p in pairs]
           for i in range(n)]
    for i in range(n):
        problem += pulp.lpSum(has[i]) == 1

    # 2. no two people have the same initials
    for k in range(len(pairs)):
        problem += pulp.lpSum(has[i][k] for i in range(n)) <= 1

    # 3. no one shares a letter with the person in front of them
    for i in range(n - 1):
        for k, p in enumerate(pairs):
            for q_index, q in enumerate(pairs):
                if set(p) & set(q):
                    problem += has[i][k] + has[i + 1][q_index] <= 1

    # BE is at the front, CD right behind, and BD at the end
    problem += has[0][pairs.index((B, E))] == 1
    problem += has[1][pairs.index((C, D))] == 1
    problem += has[n - 1][pairs.index((B, D))] == 1

    queue = [[pulp.lpSum(p[side] * has[i][k] for k, p in enumerate(pairs)) for side in (0, 1)]
             for i in range(n)]
    return problem, {"queue": queue}
