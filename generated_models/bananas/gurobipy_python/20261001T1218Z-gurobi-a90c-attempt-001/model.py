"""Bananas: buy 100 fruits of four kinds for 100 dollars, buying every kind, with as few bananas and apples as possible."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    # The puzzle has no instance data: the prices and totals are the puzzle's own,
    # mirrored from the reference.
    model = gp.Model("bananas")

    # Every kind of fruit is bought, between 1 and 100 of each.
    bananas = model.addVar(lb=1, ub=100, vtype=GRB.INTEGER, name="bananas")
    oranges = model.addVar(lb=1, ub=100, vtype=GRB.INTEGER, name="oranges")
    mangoes = model.addVar(lb=1, ub=100, vtype=GRB.INTEGER, name="mangoes")
    apples = model.addVar(lb=1, ub=100, vtype=GRB.INTEGER, name="apples")

    # 100 dollars: bananas cost 3/5, oranges 5/7, mangoes 7/9 and apples 9/3 dollars
    # each; both sides are multiplied by 3*5*7*9 = 945 to keep the coefficients integral.
    model.addConstr(3 * 189 * bananas + 5 * 135 * oranges + 7 * 105 * mangoes + 9 * 315 * apples == 100 * 945,
                    name="dollars")

    # 100 fruits in total.
    model.addConstr(bananas + oranges + mangoes + apples == 100, name="fruits")

    # Buy as few bananas and apples as possible.
    model.setObjective(bananas + apples, GRB.MINIMIZE)

    return model, {"bananas": bananas, "oranges": oranges, "mangoes": mangoes, "apples": apples}
