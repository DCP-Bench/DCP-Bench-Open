# Wolf, goat and cabbage river crossing: a farmer ferries a wolf, a goat and a cabbage
# across a river in a boat that carries the farmer and at most one item, so that the
# wolf is never left alone with the goat and the goat never alone with the cabbage.
# Each stage is one state of the river; every position is 0 (starting shore) or
# 1 (destination shore). The number of stages comes from the instance.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["stage"]
    m = Model("wolf_goat_cabbage")
    stages = range(n)
    steps = range(n - 1)

    # positions: 1 = destination shore, 0 = starting shore
    wolf = {t: m.addVar(name=f"wolf_{t}", vtype="B") for t in stages}
    goat = {t: m.addVar(name=f"goat_{t}", vtype="B") for t in stages}
    cabbage = {t: m.addVar(name=f"cabbage_{t}", vtype="B") for t in stages}
    boat = {t: m.addVar(name=f"boat_{t}", vtype="B") for t in stages}
    items = {"wolf": wolf, "goat": goat, "cabbage": cabbage}

    # all four start on the starting shore
    m.addCons(wolf[0] == 0)
    m.addCons(goat[0] == 0)
    m.addCons(cabbage[0] == 0)
    m.addCons(boat[0] == 0)

    # all four end on the destination shore
    m.addCons(wolf[n - 1] == 1)
    m.addCons(goat[n - 1] == 1)
    m.addCons(cabbage[n - 1] == 1)
    m.addCons(boat[n - 1] == 1)

    # the boat crosses at every stage: it alternates shores
    for t in steps:
        m.addCons(boat[t] + boat[t + 1] == 1)

    # the boat carries the farmer and at most one item per crossing
    moved = {(i, t): m.addVar(name=f"moved_{i}_{t}", vtype="B") for i in items for t in steps}
    for t in steps:
        # the boat takes at most one item across
        m.addCons(quicksum(moved[i, t] for i in items) <= 1)
        for i, pos in items.items():
            # an item that crosses is on the boat's shore and ends on the other shore
            m.addConsIndicator(pos[t] - boat[t] <= 0, binvar=moved[i, t])
            m.addConsIndicator(pos[t] - boat[t] >= 0, binvar=moved[i, t])
            m.addConsIndicator(pos[t + 1] + pos[t] <= 1, binvar=moved[i, t])
            m.addConsIndicator(pos[t + 1] + pos[t] >= 1, binvar=moved[i, t])
            # an item that does not cross stays on its shore
            m.addConsIndicator(pos[t + 1] - pos[t] <= 0, binvar=moved[i, t], activeone=False)
            m.addConsIndicator(pos[t + 1] - pos[t] >= 0, binvar=moved[i, t], activeone=False)

    # the wolf must not be left alone with the goat, and the goat not with the cabbage:
    # if two items share a shore, the farmer must be on that shore too
    def same_shore(a, b, label, t):
        # d = 0 exactly when a and b are on the same shore at stage t
        d = m.addVar(name=f"differ_{label}_{t}", vtype="B")
        m.addCons(d >= a[t] - b[t])
        m.addCons(d >= b[t] - a[t])
        m.addCons(d <= a[t] + b[t])
        m.addCons(d <= 2 - a[t] - b[t])
        return d

    # the wolf eats the goat when the farmer is away
    for t in stages:
        d = same_shore(wolf, goat, "wolf_goat", t)
        m.addCons(wolf[t] - boat[t] <= d)
        m.addCons(boat[t] - wolf[t] <= d)

    # the goat eats the cabbage when the farmer is away
    for t in stages:
        d = same_shore(goat, cabbage, "goat_cabbage", t)
        m.addCons(goat[t] - boat[t] <= d)
        m.addCons(boat[t] - goat[t] <= d)

    outputs = {
        "wolf_pos": [wolf[t] for t in stages],
        "goat_pos": [goat[t] for t in stages],
        "cabbage_pos": [cabbage[t] for t in stages],
        "boat_pos": [boat[t] for t in stages],
    }
    return m, outputs
