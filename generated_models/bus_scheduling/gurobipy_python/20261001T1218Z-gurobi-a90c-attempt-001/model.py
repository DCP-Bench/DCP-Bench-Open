"""Bus scheduling: choose how many buses start in each 4-hour slot of the day so that every slot's demand is covered, using as few buses as possible."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    demands = instance["demands"]  # buses needed in each 4-hour slot
    slots = range(len(demands))

    model = gp.Model("bus_scheduling")

    # x[i] is the number of buses that start working in slot i; the upper bound is the
    # reference's: the total demand.
    x = model.addVars(slots, lb=0, ub=sum(demands), vtype=GRB.INTEGER, name="x")

    # A bus works for 8 hours, so it covers its starting slot and the next one. The slots wrap
    # around the day: slot i + 1 is taken modulo the number of slots. The buses that start in
    # slot i or in the slot before it must cover the demand of slot i + 1.
    for i in slots:
        nxt = (i + 1) % len(demands)
        model.addConstr(x[i] + x[nxt] >= demands[nxt], name=f"cover[{nxt}]")

    # Use as few buses as possible.
    model.setObjective(x.sum(), GRB.MINIMIZE)

    return model, {"x": [x[i] for i in slots]}
