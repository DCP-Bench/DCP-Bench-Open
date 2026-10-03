"""Dinner: how many grandparents, parents and children make 20 people at a total cost of $20."""
import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data; the ranges, prices and totals below are
# the ones the puzzle states.


def build(instance):
    model = gp.Model("dinner")

    # "We're going out to dinner taking 1-6 grandparents, 1-10 parents and/or 1-40 children"
    grandparents = model.addVar(lb=1, ub=6, vtype=GRB.INTEGER, name="grandparents")
    parents = model.addVar(lb=1, ub=10, vtype=GRB.INTEGER, name="parents")
    children = model.addVar(lb=1, ub=40, vtype=GRB.INTEGER, name="children")

    # Grandparents cost $3, parents $2 and children $0.50, and the dinner costs
    # $20; counted in half dollars to keep the coefficients integer.
    model.addConstr(6 * grandparents + 4 * parents + 1 * children == 20 * 2, name="cost")

    # There must be 20 people at dinner.
    model.addConstr(grandparents + parents + children == 20, name="people")

    return model, {"grandparents": grandparents, "parents": parents, "children": children}
