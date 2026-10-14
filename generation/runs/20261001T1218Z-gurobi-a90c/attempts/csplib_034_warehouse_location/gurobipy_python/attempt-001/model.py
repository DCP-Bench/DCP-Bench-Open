"""Warehouse location: open warehouses and assign every store to one of them within capacity, minimising maintenance plus supply cost."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n_suppliers = instance["n_suppliers"]  # candidate warehouses
    n_stores = instance["n_stores"]
    building_cost = instance["building_cost"]  # maintenance cost of an open warehouse
    capacity = instance["capacity"]  # stores each warehouse can supply
    cost = instance["cost_matrix"]  # cost[s][w]: supply cost of store s from warehouse w
    stores = range(n_stores)
    warehouses = range(n_suppliers)

    model = gp.Model("warehouse_location")

    # assign[s, w] is 1 when warehouse w supplies store s; open_[w] is 1 when
    # warehouse w is open.
    assign = model.addVars(stores, warehouses, vtype=GRB.BINARY, name="assign")
    open_ = [model.addVar(vtype=GRB.BINARY, name=f"open[{w}]") for w in warehouses]

    # Each store is supplied by exactly one warehouse.
    for s in stores:
        model.addConstr(assign.sum(s, "*") == 1, name=f"supplied[{s}]")

    # A warehouse supplies at most its capacity of stores, and is open exactly
    # when it supplies at least one store: it supplies nothing unless open, and
    # an open warehouse supplies at least one store.
    for w in warehouses:
        load = assign.sum("*", w)
        model.addConstr(load <= capacity[w] * open_[w], name=f"capacity[{w}]")
        model.addConstr(open_[w] <= load, name=f"used[{w}]")

    # Total cost: supply costs of all stores plus maintenance of open warehouses.
    total_cost = gp.quicksum(cost[s][w] * assign[s, w] for s in stores for w in warehouses) + building_cost * gp.quicksum(open_)
    model.setObjective(total_cost, GRB.MINIMIZE)

    supplier_assignment = [gp.quicksum(w * assign[s, w] for w in warehouses) for s in stores]
    return model, {
        "total_cost": total_cost,
        "open_warehouses": open_,
        "supplier_assignment": supplier_assignment,
    }
