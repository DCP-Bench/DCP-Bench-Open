"""Fifty puzzle: knock over dummies whose numbers add up to exactly the target sum."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    values = instance["values"]
    dummies_ = range(len(values))

    model = gp.Model("fifty_puzzle")

    # dummies[i] is 1 when dummy i is knocked over.
    dummies = model.addVars(dummies_, vtype=GRB.BINARY, name="dummies")

    # The numbers on the knocked-over dummies add up to the target, neither more nor less.
    model.addConstr(gp.quicksum(values[i] * dummies[i] for i in dummies_) == instance["target_sum"],
                    name="target")

    return model, {"dummies": [dummies[i] for i in dummies_]}
