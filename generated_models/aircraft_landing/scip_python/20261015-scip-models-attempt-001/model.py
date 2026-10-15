# Aircraft landing: fix the landing time of each aircraft on a single runway, within
# its time window, so that the planes land in the given sequence with the required
# separation between consecutive landings, minimising the total penalty for landing
# before or after the target time.
from pyscipopt import Model, quicksum


def build(instance):
    earliest = instance["earliest_landing"]  # first possible landing time per plane
    latest = instance["latest_landing"]      # last possible landing time per plane
    target = instance["target_landing"]      # preferred landing time per plane
    pen_before = instance["penalty_before"]  # cost per unit of time landing early
    pen_after = instance["penalty_after"]    # cost per unit of time landing late
    sep = instance["separation_time"]        # minimum separation, [earlier][later]

    n = len(target)

    m = Model("aircraft_landing")

    # landing[i] = landing time of plane i, within its time window
    landing = [m.addVar(name=f"landing_{i}", vtype="I", lb=earliest[i], ub=latest[i])
               for i in range(n)]

    # early[i] = how far plane i lands before its target, late[i] = how far after
    early = [m.addVar(name=f"early_{i}", vtype="I", lb=0) for i in range(n)]
    late = [m.addVar(name=f"late_{i}", vtype="I", lb=0) for i in range(n)]
    for i in range(n):
        # the earliness and lateness of plane i relative to its target
        m.addCons(early[i] >= target[i] - landing[i])
        m.addCons(late[i] >= landing[i] - target[i])

    # the planes land in the fixed sequence 0, 1, ..., n-1; each later plane lands
    # at least the separation time after every earlier plane
    for i in range(n):
        for j in range(i + 1, n):
            m.addCons(landing[j] >= landing[i] + sep[i][j])

    # minimise the total penalty for early and late landings
    m.setObjective(quicksum(pen_before[i] * early[i] + pen_after[i] * late[i]
                            for i in range(n)),
                   "minimize")

    return m, {"landing_times": landing, "total_penalty": quicksum(
        pen_before[i] * early[i] + pen_after[i] * late[i] for i in range(n))}
