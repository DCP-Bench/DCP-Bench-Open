"""Five floors (Dinesman): Baker, Cooper, Fletcher, Miller and Smith live on different floors
of a five-floor house. From the clues, find who lives on which floor.

The model reports the floor (1..5) of B, C, F, M, S.
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data

    people = ["B", "C", "F", "M", "S"]
    floors = range(1, 6)

    problem = pulp.LpProblem("five_floors", pulp.LpMinimize)  # satisfaction

    # on[x][f] = 1 if person x lives on floor f; they all live on different floors
    on = {x: {f: pulp.LpVariable(f"on_{x}_{f}", cat="Binary") for f in floors} for x in people}
    for x in people:
        problem += pulp.lpSum(on[x].values()) == 1
    for f in floors:
        problem += pulp.lpSum(on[x][f] for x in people) == 1
    floor = {x: pulp.lpSum(f * var for f, var in on[x].items()) for x in people}

    # Baker does not live on the fifth floor
    problem += on["B"][5] == 0
    # Cooper does not live on the first floor
    problem += on["C"][1] == 0
    # Fletcher does not live on either the fifth or the first floor
    problem += on["F"][5] == 0
    problem += on["F"][1] == 0
    # Miller lives on a higher floor than does Cooper
    problem += floor["M"] >= floor["C"] + 1
    # Smith does not live on a floor adjacent to Fletcher's, and Fletcher not on one
    # adjacent to Cooper's
    for x, y in (("S", "F"), ("F", "C")):
        for f in floors:
            for g in (f - 1, f + 1):
                if g in floors:
                    problem += on[x][f] + on[y][g] <= 1

    return problem, floor
