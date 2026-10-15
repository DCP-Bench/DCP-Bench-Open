# Five floors puzzle: assign Baker, Cooper, Fletcher, Miller and Smith to floors 1 to 5,
# one person per floor, under the stated residence clues.
from pyscipopt import Model, quicksum

PEOPLE = ["B", "C", "F", "M", "S"]
FLOORS = [1, 2, 3, 4, 5]


def build(instance):
    m = Model()

    # x[p, f] = 1 if person p lives on floor f (one-hot encoding of the floor)
    x = {(p, f): m.addVar(name=f"x_{p}_{f}", vtype="B") for p in PEOPLE for f in FLOORS}

    # each person lives on exactly one floor
    for p in PEOPLE:
        m.addCons(quicksum(x[p, f] for f in FLOORS) == 1, name=f"one_floor_{p}")

    # they all live on different floors: each floor holds exactly one person
    for f in FLOORS:
        m.addCons(quicksum(x[p, f] for p in PEOPLE) == 1, name=f"one_person_{f}")

    # floor number of each person
    floor = {p: m.addVar(name=f"floor_{p}", vtype="I", lb=1, ub=5) for p in PEOPLE}
    for p in PEOPLE:
        m.addCons(floor[p] == quicksum(f * x[p, f] for f in FLOORS), name=f"floor_value_{p}")

    B, C, F, M, S = (floor[p] for p in PEOPLE)

    # Baker does not live on the fifth floor
    m.addCons(x["B", 5] == 0)

    # Cooper does not live on the first floor
    m.addCons(x["C", 1] == 0)

    # Fletcher does not live on either the fifth or the first floor
    m.addCons(x["F", 5] == 0)
    m.addCons(x["F", 1] == 0)

    # Miller lives on a higher floor than Cooper
    m.addCons(M >= C + 1)

    # Smith does not live on a floor adjacent to Fletcher's: |S - F| >= 2
    d_sf = m.addVar(name="smith_above_fletcher", vtype="B")
    m.addConsIndicator(S - F >= 2, binvar=d_sf)
    m.addConsIndicator(F - S >= 2, binvar=d_sf, activeone=False)

    # Fletcher does not live on a floor adjacent to Cooper's: |F - C| >= 2
    d_fc = m.addVar(name="fletcher_above_cooper", vtype="B")
    m.addConsIndicator(F - C >= 2, binvar=d_fc)
    m.addConsIndicator(C - F >= 2, binvar=d_fc, activeone=False)

    # the floors where each person lives
    outputs = {"B": B, "C": C, "F": F, "M": M, "S": S}
    return m, outputs
