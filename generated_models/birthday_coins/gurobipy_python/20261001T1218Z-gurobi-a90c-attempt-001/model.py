"""Birthday coins: 15 coins (half-crowns, shillings, sixpences) worth 1 pound 5 shillings 6 pence; how many half-crowns?"""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    # The puzzle has no instance data: coin values and totals are the puzzle's own,
    # mirrored from the reference.
    values = [30, 12, 6]                 # pence in a half-crown, a shilling, a sixpence
    total_value = 240 + 5 * 12 + 6      # 1 pound 5 shillings 6 pence, in pence
    total_coins = 15

    model = gp.Model("birthday_coins")

    # coins[i]: how many coins of type i Tommy was given.
    coins = model.addVars(len(values), lb=0, ub=total_coins, vtype=GRB.INTEGER, name="coins")

    # The coins add up to 1 pound 5 shillings 6 pence.
    model.addConstr(gp.quicksum(values[i] * coins[i] for i in range(len(values))) == total_value, name="value")

    # He was given 15 coins.
    model.addConstr(coins.sum() == total_coins, name="count")

    return model, {"half_crowns": coins[0]}
