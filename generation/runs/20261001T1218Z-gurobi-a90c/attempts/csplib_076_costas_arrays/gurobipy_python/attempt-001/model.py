"""Costas array: place n marks on an n-by-n grid, one per row and column, so that all vectors between marks differ (each row of the difference triangle is all different)."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["n"]
    positions = range(n)
    values = range(1, n + 1)
    # A difference between two marks lies in -(n-1)..n-1, the domain the
    # problem statement gives the difference triangle.
    diffs = range(-(n - 1), n)

    model = gp.Model("costas_arrays")

    # mark[i, v] is 1 when column i has its mark in row v. One mark per column
    # and one per row: costas is a permutation of 1..n.
    mark = model.addVars(positions, values, vtype=GRB.BINARY, name="mark")
    for i in positions:
        model.addConstr(mark.sum(i, "*") == 1, name=f"column[{i}]")
    for v in values:
        model.addConstr(mark.sum("*", v) == 1, name=f"row[{v}]")
    costas = [gp.quicksum(v * mark[i, v] for v in values) for i in positions]

    # Difference triangle: for each distance l, the difference
    # costas[i + l] - costas[i] at every start i. gap[l, i, d] is 1 when that
    # difference equals d, and exactly one d holds.
    gap = model.addVars(
        [(l, i, d) for l in range(1, n) for i in range(n - l) for d in diffs],
        vtype=GRB.BINARY, name="gap",
    )
    for l in range(1, n):
        for i in range(n - l):
            model.addConstr(gp.quicksum(gap[l, i, d] for d in diffs) == 1, name=f"one_gap[{l},{i}]")
            model.addConstr(
                costas[i + l] - costas[i] == gp.quicksum(d * gap[l, i, d] for d in diffs),
                name=f"gap_value[{l},{i}]",
            )

    # All entries in a row of the difference triangle are distinct: at distance
    # l, no difference value occurs at two starts. The row for distance n - 1
    # has a single entry and needs no constraint.
    for l in range(1, n - 1):
        for d in diffs:
            model.addConstr(gp.quicksum(gap[l, i, d] for i in range(n - l)) <= 1, name=f"distinct[{l},{d}]")

    return model, {"costas": costas}
