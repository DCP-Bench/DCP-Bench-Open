"""Five floors: Baker, Cooper, Fletcher, Miller and Smith each live on a different one of five floors; find which."""
import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data: five people, floors 1..5.
PEOPLE = "BCFMS"
FLOORS = range(1, 6)


def build(instance):
    model = gp.Model("session1_five_floors")

    # on[p, f] = 1 when person p lives on floor f; floor[p] reads it back.
    on = model.addVars(PEOPLE, FLOORS, vtype=GRB.BINARY, name="on")
    for p in PEOPLE:
        model.addConstr(on.sum(p, "*") == 1, name=f"one_floor[{p}]")
    floor = {p: gp.quicksum(f * on[p, f] for f in FLOORS) for p in PEOPLE}

    # They all live on different floors.
    for f in FLOORS:
        model.addConstr(on.sum("*", f) == 1, name=f"different[{f}]")

    # Baker does not live on the fifth floor.
    model.addConstr(on["B", 5] == 0, name="baker")
    # Cooper does not live on the first floor.
    model.addConstr(on["C", 1] == 0, name="cooper")
    # Fletcher lives on neither the fifth nor the first floor.
    model.addConstr(on["F", 5] + on["F", 1] == 0, name="fletcher")
    # Miller lives on a higher floor than Cooper.
    model.addConstr(floor["M"] >= floor["C"] + 1, name="miller_above_cooper")

    # Smith is not on a floor adjacent to Fletcher's, nor Fletcher on one
    # adjacent to Cooper's: the two never sit on floors f and f + 1.
    for a, b in (("S", "F"), ("F", "C")):
        for f in FLOORS:
            if f + 1 in FLOORS:
                model.addConstr(on[a, f] + on[b, f + 1] <= 1, name=f"not_adjacent[{a},{b},{f}]")
                model.addConstr(on[a, f + 1] + on[b, f] <= 1, name=f"not_adjacent[{b},{a},{f}]")

    return model, {p: floor[p] for p in PEOPLE}
