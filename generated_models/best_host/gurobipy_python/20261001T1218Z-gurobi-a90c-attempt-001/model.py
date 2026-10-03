"""Best host: seat six guests around a round table so that every guest sits only next to the two guests they get along with."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    # The puzzle has no instance data: the guests and whom each will sit next to are
    # the puzzle's own, mirrored from the reference.
    n = 6
    andrew, betty, cara, dave, erica, frank = range(n)
    prefs = [
        [dave, frank],     # Andrew
        [cara, erica],     # Betty
        [betty, frank],    # Cara
        [andrew, erica],   # Dave
        [betty, dave],     # Erica
        [andrew, cara],    # Frank
    ]
    seats = range(n)
    guests = range(n)

    model = gp.Model("best_host")

    # sits[i, g] is 1 when guest g takes seat i; every seat has one guest and every
    # guest one seat (all different).
    sits = model.addVars(seats, guests, vtype=GRB.BINARY, name="sits")
    for i in seats:
        model.addConstr(sits.sum(i, "*") == 1, name=f"seat[{i}]")
    for g in guests:
        model.addConstr(sits.sum("*", g) == 1, name=f"guest[{g}]")

    # The table is round: seat i is next to seat i+1 (mod n). Each guest sits only
    # next to guests on their own list, so two guests may be neighbours only when each
    # is on the other's list; every other pair is kept off neighbouring seats.
    for i in seats:
        j = (i + 1) % n
        for g in guests:
            for h in guests:
                if g != h and not (h in prefs[g] and g in prefs[h]):
                    model.addConstr(sits[i, g] + sits[j, h] <= 1, name=f"conflict[{i},{g},{h}]")

    # x[i]: the guest on seat i (Andrew 0 .. Frank 5).
    return model, {"x": [gp.quicksum(g * sits[i, g] for g in guests) for i in seats]}
