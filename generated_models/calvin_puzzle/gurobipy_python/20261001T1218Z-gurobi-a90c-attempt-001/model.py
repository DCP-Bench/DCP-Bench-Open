"""Calvin puzzle: number the squares of an n x n grid 1..n^2 so that each next number is three squares away in a row or column, or two squares away diagonally."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["n"]
    cells = [(i, j) for i in range(n) for j in range(n)]
    last = n * n

    # The allowed moves: three squares vertically or horizontally (Type I), or two
    # squares diagonally (Type II).
    moves = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]
    arcs = [((i, j), (i + a, j + b)) for (i, j) in cells for (a, b) in moves
            if 0 <= i + a < n and 0 <= j + b < n]

    model = gp.Model("calvin_puzzle")

    # x[c]: the number written on square c, 1..n^2.
    x = {c: model.addVar(lb=1, ub=last, vtype=GRB.INTEGER, name=f"x[{c[0]},{c[1]}]") for c in cells}

    # next_[c, d] is 1 when the number after the one on square c is written on square d.
    # Successor arcs between squares a move apart are far fewer variables than a
    # one-hot position for every number.
    next_ = {(c, d): model.addVar(vtype=GRB.BINARY, name=f"next[{c},{d}]") for (c, d) in arcs}

    # Every square is followed by at most one square and preceded by at most one, and
    # exactly n^2 - 1 steps are taken, so the steps form one path through all squares.
    for c in cells:
        model.addConstr(gp.quicksum(next_[a] for a in arcs if a[0] == c) <= 1, name=f"out[{c}]")
        model.addConstr(gp.quicksum(next_[a] for a in arcs if a[1] == c) <= 1, name=f"in[{c}]")
    model.addConstr(gp.quicksum(next_.values()) == last - 1, name="steps")

    # Each step goes from a number k to k + 1, which also rules out closed cycles.
    for (c, d) in arcs:
        model.addConstr((next_[c, d] == 1) >> (x[d] == x[c] + 1), name=f"step[{c},{d}]")

    # The path starts at 1: a square with no predecessor holds 1. Together with the
    # single path this makes the numbers 1..n^2 all different.
    for c in cells:
        into = gp.quicksum(next_[a] for a in arcs if a[1] == c)
        model.addConstr(x[c] <= 1 + (last - 1) * into, name=f"start[{c}]")

    return model, {"x": [[x[i, j] for j in range(n)] for i in range(n)]}
