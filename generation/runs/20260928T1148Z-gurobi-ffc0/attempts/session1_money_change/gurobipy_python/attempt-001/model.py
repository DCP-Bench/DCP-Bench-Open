"""Money change: pay the amount exactly from the coins available, using as few coins as possible."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    values = instance["types_of_coins"]      # value of each type of coin
    available = instance["available_coins"]  # how many coins of each type Alice has
    kinds = range(len(values))

    model = gp.Model("money_change")

    # coin_counts[i] is how many coins of type i Alice gives, at most the number
    # she has of that type.
    coin_counts = model.addVars(kinds, lb=0, vtype=GRB.INTEGER, name="coin_counts")
    for i in kinds:
        coin_counts[i].UB = available[i]

    # The coins given add up to the amount owed.
    model.addConstr(gp.quicksum(values[i] * coin_counts[i] for i in kinds) == instance["amount"],
                    name="amount")

    # Minimise the number of coins given.
    model.setObjective(coin_counts.sum(), GRB.MINIMIZE)

    return model, {"coin_counts": [coin_counts[i] for i in kinds]}
