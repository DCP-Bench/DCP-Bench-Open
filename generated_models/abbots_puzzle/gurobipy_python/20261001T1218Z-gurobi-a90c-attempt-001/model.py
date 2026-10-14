"""Abbot's puzzle: 100 bushels shared among 100 people, 3 per man, 2 per woman, half per child, with five times as many women as men."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    # The puzzle has no instance data: the numbers below are the puzzle's own
    # constants, mirrored from the reference.
    people = 100
    bushels = 100

    model = gp.Model("abbots_puzzle")

    men = model.addVar(lb=0, ub=people, vtype=GRB.INTEGER, name="men")
    women = model.addVar(lb=0, ub=people, vtype=GRB.INTEGER, name="women")
    children = model.addVar(lb=0, ub=people, vtype=GRB.INTEGER, name="children")

    # There are 100 people in total.
    model.addConstr(men + women + children == people, name="people")

    # 100 bushels: 3 per man, 2 per woman and half per child, doubled to stay integral.
    model.addConstr(6 * men + 4 * women + children == 2 * bushels, name="bushels")

    # Five times as many women as men.
    model.addConstr(women == 5 * men, name="women")

    return model, {"men": men, "women": women, "children": children}
