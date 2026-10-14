"""Initials queue: order ten people, whose initials are distinct ordered pairs of A-E, so that neighbours share no letter."""
import itertools

import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data. Letters A..E are 0..4; the queue length
# and the three known positions come from the statement.
N = 10
LETTERS = range(5)
A, B, C, D, E = LETTERS
KNOWN = {0: (B, E), 1: (C, D), N - 1: (B, D)}   # BE at the front, CD behind, BD at the end


def build(instance):
    model = gp.Model("initials_queue")

    # Each person's initials are two distinct letters in alphabetical order.
    pairs = list(itertools.combinations(LETTERS, 2))

    # has[i, p] = 1 when person i has initials pairs[p].
    has = model.addVars(N, len(pairs), vtype=GRB.BINARY, name="has")
    for i in range(N):
        model.addConstr(has.sum(i, "*") == 1, name=f"one_pair[{i}]")

    # No two people have the same initials.
    for p in range(len(pairs)):
        model.addConstr(has.sum("*", p) <= 1, name=f"distinct[{p}]")

    # No one shares a letter with the person in front of them: each letter is
    # used by at most one of two neighbours.
    def uses(i, letter):
        return gp.quicksum(has[i, p] for p, pair in enumerate(pairs) if letter in pair)

    for i in range(N - 1):
        for letter in LETTERS:
            model.addConstr(uses(i, letter) + uses(i + 1, letter) <= 1, name=f"no_shared[{i},{letter}]")

    # BE is at the front, CD right behind, BD at the end.
    for i, pair in KNOWN.items():
        model.addConstr(has[i, pairs.index(pair)] == 1, name=f"known[{i}]")

    queue = [[gp.quicksum(pairs[p][k] * has[i, p] for p in range(len(pairs))) for k in range(2)]
             for i in range(N)]
    return model, {"queue": queue}
