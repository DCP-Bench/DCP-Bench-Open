"""Bus driver scheduling: choose shifts so that every piece of work is covered by exactly one chosen shift, using as few shifts as possible."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    num_work = instance["num_work"]  # number of pieces of work
    num_shifts = instance["num_shifts"]  # number of candidate shifts
    shifts = instance["shifts"]  # shifts[i] lists the pieces of work shift i covers

    model = gp.Model("bus_driver_scheduling")

    # x[i] is 1 when shift i is selected.
    x = [model.addVar(vtype=GRB.BINARY, name=f"x[{i}]") for i in range(num_shifts)]

    # Each piece of work is covered by exactly one selected shift (set partitioning).
    for task in range(num_work):
        model.addConstr(
            gp.quicksum(x[i] for i in range(num_shifts) if task in shifts[i]) == 1,
            name=f"cover[{task}]",
        )

    # Every shift costs the same: minimise the number of shifts used.
    model.setObjective(gp.quicksum(x), GRB.MINIMIZE)

    return model, {"x": x}
