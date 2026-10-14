"""Car sequencing: order the cars on an assembly line so that no station sees more than its share of cars needing its option."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    at_most = instance["at_most"]      # per option: how many cars in a window may need it
    per_slots = instance["per_slots"]  # per option: the window length
    demand = instance["demand"]        # per car type: how many cars are to be built
    requires = instance["requires"]    # per car type: 0/1 for each option
    n_cars = sum(demand)
    n_types = len(demand)
    n_options = len(at_most)
    slots = range(n_cars)
    types = range(n_types)

    model = gp.Model("car_sequencing")

    # place[s, t] is 1 when the car in slot s is of type t. A one-hot assignment is the
    # linear form of the reference's sequence[s] == t; it needs n_cars * n_types binaries.
    place = model.addVars(slots, types, vtype=GRB.BINARY, name="place")

    # Every slot holds exactly one car.
    for s in slots:
        model.addConstr(place.sum(s, "*") == 1, name=f"one_car[{s}]")

    # The number of cars of each type in the sequence equals the demand for that type.
    for t in types:
        model.addConstr(place.sum("*", t) == demand[t], name=f"demand[{t}]")

    # No station is overloaded: in every window of per_slots[o] consecutive slots, at most
    # at_most[o] cars need option o.
    for o in range(n_options):
        needing = [t for t in types if requires[t][o]]
        for s in range(n_cars - per_slots[o] + 1):
            model.addConstr(
                gp.quicksum(place[k, t] for k in range(s, s + per_slots[o]) for t in needing)
                <= at_most[o], name=f"window[{o},{s}]")

    # The type of the car in each slot, read back from the assignment.
    return model, {"sequence": [gp.quicksum(t * place[s, t] for t in types) for s in slots]}
