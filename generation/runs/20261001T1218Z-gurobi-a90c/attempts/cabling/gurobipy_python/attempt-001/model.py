"""Cabling: put n devices in distinct rack positions so that the total length of the cables joining them is as short as possible."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["n"]                    # number of devices, and of rack positions
    devices = instance["devices"]        # device names
    cable_struct = instance["cable_struct"]  # each cable: [device name, device name, number of cables]
    positions = range(n)

    model = gp.Model("cabling")

    device_index = {name: i for i, name in enumerate(devices)}
    cables = [(device_index[a], device_index[b], num) for a, b, num in cable_struct]

    # put[d, p] is 1 when device d stands in rack position p; every device has its own position.
    put = model.addVars(n, positions, vtype=GRB.BINARY, name="put")
    for d in range(n):
        model.addConstr(put.sum(d, "*") == 1, name=f"one_position[{d}]")
    for p in positions:
        model.addConstr(put.sum("*", p) == 1, name=f"one_device[{p}]")
    x = [gp.quicksum(p * put[d, p] for p in positions) for d in range(n)]  # position of device d

    # The length of the cables between two devices is the distance between their positions
    # times the number of cables. gp.abs_ takes a variable, so the signed distance gets one.
    lengths = []
    for k, (a, b, num) in enumerate(cables):
        signed = model.addVar(lb=-(n - 1), ub=n - 1, vtype=GRB.INTEGER, name=f"signed[{k}]")
        distance = model.addVar(lb=0, ub=n - 1, vtype=GRB.INTEGER, name=f"distance[{k}]")
        model.addConstr(signed == x[a] - x[b], name=f"signed[{k}]")
        model.addConstr(distance == gp.abs_(signed), name=f"distance[{k}]")
        lengths.append(num * distance)

    # Total cable length, to be minimised.
    final_sum = gp.quicksum(lengths)
    model.setObjective(final_sum, GRB.MINIMIZE)

    return model, {"final_sum": final_sum}
