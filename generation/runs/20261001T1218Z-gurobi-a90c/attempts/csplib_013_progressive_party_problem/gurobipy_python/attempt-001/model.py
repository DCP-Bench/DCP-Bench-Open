"""Progressive party: some boats host and the other crews visit hosts over several periods, never exceeding a host's capacity and never meeting another crew twice; use as few hosts as possible."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n_boats = instance["n_boats"]
    n_periods = instance["n_periods"]
    capacity = instance["capacity"]    # per boat: how many people it can hold
    crew_size = instance["crew_size"]  # per boat: how many people its crew has
    boats = range(n_boats)
    periods = range(n_periods)

    model = gp.Model("progressive_party")

    # is_host[b] is 1 when boat b is a host boat.
    is_host = model.addVars(boats, vtype=GRB.BINARY, name="is_host")

    # at[p, c, h] is 1 when the crew of boat c is on boat h in period p (a host's crew stays on
    # its own boat). One-hot form of the reference's visits[p][c] == h.
    at = model.addVars(periods, boats, boats, vtype=GRB.BINARY, name="at")
    for p in periods:
        for c in boats:
            model.addConstr(at.sum(p, c, "*") == 1, name=f"one_boat[{p},{c}]")
    visits = [[gp.quicksum(h * at[p, c, h] for h in boats) for c in boats] for p in periods]

    # Crews of host boats stay on their boat in every period.
    for b in boats:
        for p in periods:
            model.addConstr(at[p, b, b] >= is_host[b], name=f"host_stays[{p},{b}]")

    for p in periods:
        for h in boats:
            # Non-host boats cannot be visited: only a host can have any crew on board.
            model.addConstr(at.sum(p, "*", h) <= n_boats * is_host[h], name=f"only_hosts[{p},{h}]")
            # The people on a boat never exceed its capacity.
            model.addConstr(gp.quicksum(crew_size[c] * at[p, c, h] for c in boats) <= capacity[h],
                            name=f"capacity[{p},{h}]")

    # A guest crew cannot visit a boat twice. A host crew sits on its own boat in every period,
    # so for a host the bound is relaxed to the number of periods.
    for c in boats:
        for h in boats:
            model.addConstr(at.sum("*", c, h) <= 1 + (n_periods - 1) * is_host[c], name=f"once[{c},{h}]")

    # Crews cannot meet more than once: two crews meet in period p when they are on the same
    # boat. same[p, a, b] must be 1 when visits[p][a] == visits[p][b]; otherwise the two boats
    # differ, in one direction or the other (higher says which), by at least 1. M = n_boats
    # makes the relaxed direction inactive.
    for a in boats:
        for b in range(a + 1, n_boats):
            met = []
            for p in periods:
                same = model.addVar(vtype=GRB.BINARY, name=f"same[{p},{a},{b}]")
                higher = model.addVar(vtype=GRB.BINARY, name=f"higher[{p},{a},{b}]")
                model.addConstr(visits[p][a] - visits[p][b] + n_boats * same - n_boats * higher
                                >= 1 - n_boats, name=f"apart_up[{p},{a},{b}]")
                model.addConstr(visits[p][b] - visits[p][a] + n_boats * same + n_boats * higher >= 1,
                                name=f"apart_down[{p},{a},{b}]")
                met.append(same)
            model.addConstr(gp.quicksum(met) <= 1, name=f"meet_once[{a},{b}]")

    # Use as few host boats as possible.
    model.setObjective(is_host.sum(), GRB.MINIMIZE)

    return model, {"visits": visits, "is_host": [is_host[b] for b in boats]}
