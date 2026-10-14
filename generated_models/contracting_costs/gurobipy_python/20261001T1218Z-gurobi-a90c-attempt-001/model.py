"""Contracting costs: find what each of six tradesmen charges from what pairs of them charge together."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    # The puzzle has no instance data: the pairs, their totals and the range 1..5300
    # are the puzzle's own, mirrored from the reference.
    names = ["paper_hanger", "painter", "plumber", "electrician", "carpenter", "mason"]

    model = gp.Model("contracting_costs")

    # charge[p]: what tradesman p charges, in dollars.
    charge = {p: model.addVar(lb=1, ub=5300, vtype=GRB.INTEGER, name=p) for p in names}

    # What the contractor pays each pair together.
    pairs = [
        ("paper_hanger", "painter", 1100),
        ("painter", "plumber", 1700),
        ("plumber", "electrician", 1100),
        ("electrician", "carpenter", 3300),
        ("carpenter", "mason", 5300),
        ("mason", "painter", 3200),
    ]
    for p, q, total in pairs:
        model.addConstr(charge[p] + charge[q] == total, name=f"pay[{p},{q}]")

    return model, charge
