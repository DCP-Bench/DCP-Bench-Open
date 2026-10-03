"""Golomb ruler: place marks on a ruler so that all distances between pairs of marks are different, making the ruler as short as possible."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    size = instance["size"]  # number of marks
    marks_ = range(size)

    model = gp.Model("golomb_rulers")

    # marks[i] is the position of mark i; positions run from 0 to size * size (the reference's bound).
    marks = model.addVars(marks_, lb=0, ub=size * size, vtype=GRB.INTEGER, name="marks")

    # The first mark is at 0 and the marks are strictly increasing.
    model.addConstr(marks[0] == 0, name="first_is_zero")
    for i in range(size - 1):
        model.addConstr(marks[i + 1] >= marks[i] + 1, name=f"increasing[{i}]")

    # The distance between marks i < j is marks[j] - marks[i]. The k distances between
    # consecutive marks inside any k + 1 of them are distinct positive whole numbers, so they
    # sum to at least 1 + 2 + ... + k. This is implied by the all-different rule below and is
    # added only to give the solver a bound on the length.
    for i in range(size):
        for j in range(i + 1, size):
            k = j - i
            model.addConstr(marks[j] - marks[i] >= k * (k + 1) // 2, name=f"min_distance[{i},{j}]")

    # All distances are different. Two distances are different automatically when they share
    # their lower mark or their upper mark (the other marks differ, since marks increase), so
    # only pairs of distances with no common lower and no common upper mark are posted.
    # For each such pair a binary picks which distance is larger, and an indicator constraint
    # then enforces a gap of at least 1 in that direction.
    pairs = [(i, j) for i in range(size) for j in range(i + 1, size)]
    for p, (i, j) in enumerate(pairs):
        for (k, l) in pairs[p + 1:]:
            if i == k or j == l:
                continue
            first_larger = model.addVar(vtype=GRB.BINARY, name=f"larger[{i},{j},{k},{l}]")
            difference = (marks[j] - marks[i]) - (marks[l] - marks[k])
            model.addConstr((first_larger == 1) >> (difference >= 1), name=f"gt[{i},{j},{k},{l}]")
            model.addConstr((first_larger == 0) >> (difference <= -1), name=f"lt[{i},{j},{k},{l}]")

    # Find the shortest ruler: its length is the position of the last mark.
    length = marks[size - 1]
    model.setObjective(length, GRB.MINIMIZE)

    return model, {"marks": [marks[i] for i in marks_], "length": length}
