"""Hidato: fill the grid with 1..r*c, keeping the given numbers, so that every two consecutive numbers sit in cells touching horizontally, vertically or diagonally."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    puzzle = instance["puzzle"]  # given numbers; 0 marks an empty cell
    r = len(puzzle)
    c = len(puzzle[0])
    N = r * c
    cells = [(i, j) for i in range(r) for j in range(c)]

    model = gp.Model("hidato")

    # x[i, j] is the number in cell (i, j), from 1..r*c; the given numbers stay.
    x = {}
    for (i, j) in cells:
        given = puzzle[i][j]
        lo, hi = (given, given) if given > 0 else (1, N)
        x[i, j] = model.addVar(lb=lo, ub=hi, vtype=GRB.INTEGER, name=f"x[{i},{j}]")

    # The numbers are placed as a chain 1, 2, ..., r*c, each next number in a
    # touching cell. next_[p, q] is 1 when cell q holds the number after the one
    # in cell p; it exists only for touching cells (a king's move apart). A
    # one-hot of every number in every cell would need (r*c)**2 binaries,
    # beyond the licence's 2000-variable limit at 12-by-12.
    next_ = {}
    for (i, j) in cells:
        for a in (-1, 0, 1):
            for b in (-1, 0, 1):
                if (a, b) != (0, 0) and 0 <= i + a < r and 0 <= j + b < c:
                    next_[(i, j), (i + a, j + b)] = model.addVar(
                        vtype=GRB.BINARY, name=f"next[{i},{j},{i + a},{j + b}]")

    # When q follows p, the number in q is one more than the number in p.
    for (p, q), arc in next_.items():
        model.addConstr((arc == 1) >> (x[q] == x[p] + 1), name=f"consecutive[{p},{q}]")

    # Each cell has at most one successor and at most one predecessor, and the
    # chain has r*c - 1 links. Numbers grow along every link, so the links hold
    # no loop and form a single chain through all cells; its r*c numbers are
    # consecutive within 1..r*c, so they are all different and start at 1.
    for p in cells:
        model.addConstr(gp.quicksum(arc for (s, _), arc in next_.items() if s == p) <= 1, name=f"successor[{p}]")
        model.addConstr(gp.quicksum(arc for (_, t), arc in next_.items() if t == p) <= 1, name=f"predecessor[{p}]")
    model.addConstr(gp.quicksum(next_.values()) == N - 1, name="chain_length")

    return model, {"x": [[x[i, j] for j in range(c)] for i in range(r)]}
