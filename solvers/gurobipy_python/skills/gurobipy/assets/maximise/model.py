"""Maximise: integer production plan for two products under two resource limits."""
import gurobipy as gp
from gurobipy import GRB

profit = {"A": 5, "B": 4}
hours = {"A": 6, "B": 4}     # machine hours per batch
labour = {"A": 1, "B": 2}    # labour units per batch

model = gp.Model("plan")
model.Params.OutputFlag = 0
batches = model.addVars(profit, vtype=GRB.INTEGER, lb=0, name="batches")
model.addConstr(gp.quicksum(hours[p] * batches[p] for p in profit) <= 24, name="machine")
model.addConstr(gp.quicksum(labour[p] * batches[p] for p in profit) <= 6, name="labour")
model.setObjective(gp.quicksum(profit[p] * batches[p] for p in profit), GRB.MAXIMIZE)
model.optimize()

if model.Status == GRB.OPTIMAL:
    print("Profit:", round(model.ObjVal))
    print("Batches:", {p: round(batches[p].X) for p in profit})
else:
    print("Status:", model.Status)
