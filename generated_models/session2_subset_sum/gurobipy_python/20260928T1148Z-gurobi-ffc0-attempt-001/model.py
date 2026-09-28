"""Subset sum: find how many bags of each size the thieves took, given the total number of coins lost."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    total = instance["total_coins_lost"]
    coins = instance["coin_numbers"]  # coins[i]: coins in a bag of type i
    kinds = range(len(coins))

    model = gp.Model("subset_sum")

    # bags[i] is the number of bags of type i stolen; the reference bounds it by
    # the total number of coins lost.
    bags = model.addVars(kinds, lb=0, ub=total, vtype=GRB.INTEGER, name="bags")

    # The coins in the stolen bags add up to the coins lost.
    model.addConstr(gp.quicksum(coins[i] * bags[i] for i in kinds) == total, name="total")

    return model, {"bags": [bags[i] for i in kinds]}
