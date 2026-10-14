"""Langford's problem: arrange two copies of each number 1..k in a sequence of 2k places so
that the two copies of the number i have exactly i numbers between them (they are i + 1
places apart).

The model reports the sequence.
"""
import pulp


def build(instance):
    k = instance["k"]
    length = 2 * k  # number of places in the sequence

    problem = pulp.LpProblem("langford", pulp.LpMinimize)  # satisfaction: no objective

    # start[i][p] = 1 if the first copy of number i is at place p; its second copy is
    # then at place p + i + 1. Only starts that leave room for the second copy exist.
    # Stating the pair positions directly gives an exact cover of the places, which has
    # far fewer variables than comparing the positions of every pair of places.
    start = {i: {p: pulp.LpVariable(f"start_{i}_{p}", cat="Binary")
                 for p in range(length - i - 1)}
             for i in range(1, k + 1)}

    # the two copies of each number i are placed exactly once, i + 1 places apart
    for i in range(1, k + 1):
        problem += pulp.lpSum(start[i].values()) == 1

    # every place of the sequence holds exactly one number: it is the first copy of some
    # number i (start at that place) or the second copy (start i + 1 places earlier)
    holds = []
    for place in range(length):
        covering = []
        for i in range(1, k + 1):
            if place in start[i]:
                covering.append((i, start[i][place]))
            if place - i - 1 in start[i]:
                covering.append((i, start[i][place - i - 1]))
        problem += pulp.lpSum(var for _, var in covering) == 1
        # the number written at this place
        holds.append(pulp.lpSum(i * var for i, var in covering))

    return problem, {"sol": holds}
