"""Schur's lemma: put balls 1..n into c boxes so that no x + y = z triple lies entirely in one box."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n, c = instance["n"], instance["c"]
    balls = range(1, n + 1)
    boxes = range(1, c + 1)

    model = gp.Model("schurs_lemma")

    # inbox[i, j] is 1 when ball i is in box j.
    inbox = model.addVars(balls, boxes, vtype=GRB.BINARY, name="inbox")

    # Every ball is in exactly one box.
    for i in balls:
        model.addConstr(inbox.sum(i, "*") == 1, name=f"one_box[{i}]")

    # For every x + y = z, the three balls are not all in the same box. When
    # x == y the ball is counted twice, which forbids x and z sharing a box, as
    # the reference's pairwise disequalities do.
    for x in range(1, n):
        for y in range(1, n - x + 1):
            z = x + y
            for j in boxes:
                model.addConstr(inbox[x, j] + inbox[y, j] + inbox[z, j] <= 2, name=f"triple[{x},{y},{j}]")

    # The box of each ball, read back from the assignment.
    return model, {"balls": [gp.quicksum(j * inbox[i, j] for j in boxes) for i in balls]}
