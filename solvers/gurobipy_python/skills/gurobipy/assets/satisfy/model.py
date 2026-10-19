"""Satisfy: pay exactly 50 with 3, 5 and 7 coins, using at most 10 coins."""
import gurobipy as gp
from gurobipy import GRB

model = gp.Model("coins")
model.Params.OutputFlag = 0
coins = {3: model.addVar(vtype=GRB.INTEGER, name="c3"),
         5: model.addVar(vtype=GRB.INTEGER, name="c5"),
         7: model.addVar(vtype=GRB.INTEGER, name="c7")}
model.addConstr(gp.quicksum(v * c for v, c in coins.items()) == 50, name="total")
model.addConstr(gp.quicksum(coins.values()) <= 10, name="count")
# No setObjective call: Gurobi treats this as a satisfaction problem.
model.optimize()

if model.Status == GRB.OPTIMAL:
    print("Coins:", {v: round(c.X) for v, c in coins.items()})
    print("Total value:", sum(v * round(c.X) for v, c in coins.items()))
else:
    print("Status:", model.Status)
