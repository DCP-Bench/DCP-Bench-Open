"""Infeasible: two shifts of at most 3 people cannot cover a demand of 7."""
import gurobipy as gp
from gurobipy import GRB

SHIFTS, CAP, DEMAND = 2, 3, 7

model = gp.Model("staffing")
model.Params.OutputFlag = 0
staff = model.addVars(SHIFTS, vtype=GRB.INTEGER, lb=0, ub=CAP, name="staff")
model.addConstr(staff.sum() >= DEMAND, name="demand")
model.optimize()

if model.Status == GRB.INFEASIBLE:
    print("Status: INFEASIBLE")
    model.computeIIS()  # smallest set of constraints and bounds that conflicts
    conflict = [c.ConstrName for c in model.getConstrs() if c.IISConstr]
    print("Conflicting constraints:", sorted(conflict))
else:
    print("Status:", model.Status)
