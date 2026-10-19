# Five floors puzzle (session1_five_floors): Baker (B), Cooper (C), Fletcher (F),
# Miller (M) and Smith (S) live on the first five floors of an apartment house.
# Output: the floor of each person, numbered 1 to 5, as B, C, F, M, S.
import mip

PEOPLE = ["B", "C", "F", "M", "S"]
FLOORS = [1, 2, 3, 4, 5]
LOW, HIGH = FLOORS[0], FLOORS[-1]
# Largest possible difference between two floors, plus slack: a valid big-M.
M = (HIGH - LOW) + 2


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # They all live on different floors: each person has exactly one floor,
    # and each floor holds exactly one person.
    on = {}
    for p in PEOPLE:
        for f in FLOORS:
            on[p, f] = model.add_var(f"on_{p}_{f}", var_type=mip.BINARY)
    floor = {}
    for p in PEOPLE:
        model.add_constr(mip.xsum(on[p, f] for f in FLOORS) == 1)
        floor[p] = model.add_var(f"floor_{p}", lb=LOW, ub=HIGH, var_type=mip.INTEGER)
        model.add_constr(floor[p] == mip.xsum(f * on[p, f] for f in FLOORS))
    for f in FLOORS:
        model.add_constr(mip.xsum(on[p, f] for p in PEOPLE) == 1)

    # Baker does not live on the fifth floor.
    model.add_constr(floor["B"] <= HIGH - 1)

    # Cooper does not live on the first floor.
    model.add_constr(floor["C"] >= LOW + 1)

    # Fletcher does not live on either the fifth or the first floor.
    model.add_constr(floor["F"] >= LOW + 1)
    model.add_constr(floor["F"] <= HIGH - 1)

    # Miller lives on a higher floor than does Cooper.
    model.add_constr(floor["M"] >= floor["C"] + 1)

    # Smith does not live on a floor adjacent to Fletcher's.
    # Fletcher's and Smith's floors differ by at least 2: s = 1 means S is below F.
    s_sf = model.add_var("s_sf", var_type=mip.BINARY)
    model.add_constr(floor["S"] - floor["F"] <= -2 + M * (1 - s_sf))
    model.add_constr(floor["S"] - floor["F"] >= 2 - M * s_sf)

    # Fletcher does not live on a floor adjacent to Cooper's.
    # Fletcher's and Cooper's floors differ by at least 2: s = 1 means F is below C.
    s_fc = model.add_var("s_fc", var_type=mip.BINARY)
    model.add_constr(floor["F"] - floor["C"] <= -2 + M * (1 - s_fc))
    model.add_constr(floor["F"] - floor["C"] >= 2 - M * s_fc)

    return model, {
        "B": floor["B"],
        "C": floor["C"],
        "F": floor["F"],
        "M": floor["M"],
        "S": floor["S"],
    }
