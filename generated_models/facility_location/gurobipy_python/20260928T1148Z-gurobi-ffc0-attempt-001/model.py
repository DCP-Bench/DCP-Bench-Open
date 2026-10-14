"""Facility location: open warehouses and ship to regions at the least weekly cost, under three opening rules."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    fixed_costs = instance["fixed_costs"]
    shipping_costs = instance["shipping_costs"]  # shipping_costs[i][j]: per unit, warehouse i to region j
    demands = instance["demands"]
    max_shipping = instance["max_shipping"]
    warehouses = range(len(instance["warehouse_s"]))
    regions = range(len(demands))
    # The warehouses are, in order, New York, Los Angeles, Chicago and Atlanta.
    new_york, los_angeles, chicago, atlanta = warehouses

    model = gp.Model("facility_location")

    # open_warehouse[i] is 1 when warehouse i is open; ships[i, j] is the units
    # it sends to region j each week.
    open_warehouse = model.addVars(warehouses, vtype=GRB.BINARY, name="open_warehouse")
    ships = model.addVars(warehouses, regions, lb=0, ub=max_shipping, vtype=GRB.INTEGER, name="ships")

    # A warehouse ships at most max_shipping units a week, and nothing when closed.
    for i in warehouses:
        model.addConstr(ships.sum(i, "*") <= max_shipping * open_warehouse[i], name=f"shipping[{i}]")

    # Every region receives at least its weekly demand.
    for j in regions:
        model.addConstr(ships.sum("*", j) >= demands[j], name=f"demand[{j}]")

    # 1. If the New York warehouse is opened, the Los Angeles one is opened too.
    model.addConstr(open_warehouse[new_york] <= open_warehouse[los_angeles], name="new_york_needs_la")
    # 2. At most three warehouses are open.
    model.addConstr(open_warehouse.sum() <= 3, name="at_most_three")
    # 3. The Atlanta or the Los Angeles warehouse is open.
    model.addConstr(open_warehouse[atlanta] + open_warehouse[los_angeles] >= 1, name="atlanta_or_la")

    # total_cost is the fixed cost of the open warehouses plus the shipping cost.
    # The reference model gives it the domain 0..10000, which is mirrored here.
    total_cost = model.addVar(lb=0, ub=10000, vtype=GRB.INTEGER, name="total_cost")
    model.addConstr(total_cost == gp.quicksum(fixed_costs[i] * open_warehouse[i] for i in warehouses)
                    + gp.quicksum(shipping_costs[i][j] * ships[i, j] for i in warehouses for j in regions),
                    name="cost")

    # Minimise the total cost.
    model.setObjective(total_cost, GRB.MINIMIZE)

    return model, {"total_cost": total_cost,
                   "open_warehouse": [open_warehouse[i] for i in warehouses],
                   "ships": [[ships[i, j] for j in regions] for i in warehouses]}
