"""Circling the squares: ten different numbers in a circle where the squares of any two adjacent numbers sum to the squares of the two diametrically opposite."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    # The puzzle has no instance data: the range 1..99 (no number has more than two
    # figures), the circle and the four given numbers are the puzzle's own, mirrored
    # from the reference.
    names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K"]
    given = {"A": 16, "B": 2, "F": 8, "G": 14}
    values = range(1, 100)

    model = gp.Model("circling_squares")
    # Squares reach 99^2 = 9801; tighten the integrality tolerance so a binary cannot
    # carry a fraction of such a coefficient.
    model.Params.IntFeasTol = 1e-9

    # is_[p, v] is 1 when square p holds the number v; this makes the squares linear.
    is_ = model.addVars(names, values, vtype=GRB.BINARY, name="is")
    for p in names:
        model.addConstr(is_.sum(p, "*") == 1, name=f"one_number[{p}]")
    number = {p: gp.quicksum(v * is_[p, v] for v in values) for p in names}
    square = {p: gp.quicksum(v * v * is_[p, v] for v in values) for p in names}

    # Every square holds a different number.
    for v in values:
        model.addConstr(is_.sum("*", v) <= 1, name=f"different[{v}]")

    # The four example numbers stand as they are: A = 16, B = 2, F = 8, G = 14.
    for p, v in given.items():
        model.addConstr(is_[p, v] == 1, name=f"given[{p}]")

    # Two adjacent squares and the two diametrically opposite have equal sums of
    # squares: A,B with F,G; B,C with G,H; C,D with H,I; D,E with I,K; E,F with K,A.
    for (p, q, r, s) in [("A", "B", "F", "G"), ("B", "C", "G", "H"), ("C", "D", "H", "I"),
                         ("D", "E", "I", "K"), ("E", "F", "K", "A")]:
        model.addConstr(square[p] + square[q] == square[r] + square[s], name=f"opposite[{p}{q}]")

    return model, number
