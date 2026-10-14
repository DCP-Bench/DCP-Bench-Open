# Water buckets: pour water between buckets so that the 8-pint and the 5-pint
# bucket each end with 4 pints. Minimise the number of pours.
from pyscipopt import Model, quicksum


def build(instance):
    caps = instance["capacities"]  # bucket capacities
    init = instance["initial_state"]  # water in each bucket at the start
    goal = instance["goal_state"]  # water in each bucket at the goal
    steps = instance["MAX_STEPS"]  # length of the output sequence; index 0 is the start
    pad = instance["PADDING_VALUE"]  # value used after the goal is reached

    K = len(caps)
    T = steps - 1  # at most MAX_STEPS - 1 pours
    cmax = max(caps)  # big-M for the pour amounts

    m = Model("water_buckets")

    # s[t][k]: pints in bucket k after t pours
    s = [
        [m.addVar(name=f"s_{t}_{k}", vtype="I", lb=0, ub=caps[k]) for k in range(K)]
        for t in range(T + 1)
    ]
    # done[t] = 1 once the goal state has been reached after t pours
    done = [m.addVar(name=f"done_{t}", vtype="B") for t in range(T + 1)]

    # the start state is the initial state
    for k in range(K):
        m.addCons(s[0][k] == init[k])

    # once reached, the goal state stays reached
    for t in range(T):
        m.addCons(done[t] <= done[t + 1])
    m.addCons(done[T] == 1)

    # a state marked as done is the goal state
    for t in range(T + 1):
        for k in range(K):
            m.addConsIndicator(s[t][k] <= goal[k], binvar=done[t])
            m.addConsIndicator(s[t][k] >= goal[k], binvar=done[t])

    # total water is conserved
    total = sum(init)
    for t in range(T + 1):
        m.addCons(quicksum(s[t][k] for k in range(K)) == total)

    # pour[t, i, j]: pour from bucket i into bucket j at step t
    # amt[t, i, j]: pints poured
    # emp[t, i, j]: the pour empties bucket i; full[t, i, j]: the pour fills bucket j
    pairs = [(i, j) for i in range(K) for j in range(K) if i != j]
    y, amt, emp, full = {}, {}, {}, {}
    for t in range(1, T + 1):
        for i, j in pairs:
            y[t, i, j] = m.addVar(name=f"pour_{t}_{i}_{j}", vtype="B")
            amt[t, i, j] = m.addVar(name=f"amt_{t}_{i}_{j}", vtype="I", lb=0, ub=cmax)
            emp[t, i, j] = m.addVar(name=f"emp_{t}_{i}_{j}", vtype="B")
            full[t, i, j] = m.addVar(name=f"full_{t}_{i}_{j}", vtype="B")

    for t in range(1, T + 1):
        prev, cur = s[t - 1], s[t]

        # one pour per step until the goal is reached, none afterwards
        m.addCons(quicksum(y[t, i, j] for i, j in pairs) == 1 - done[t - 1])

        for i, j in pairs:
            a = amt[t, i, j]
            p = y[t, i, j]
            # a pour is either a pour that empties the source or one that fills the target
            m.addCons(emp[t, i, j] + full[t, i, j] == p)
            # a pour cannot exceed what the source holds or the room left in the target
            m.addCons(a <= prev[i])
            m.addCons(a <= caps[j] - prev[j])
            # an emptying pour moves all of the source
            m.addConsIndicator(a >= prev[i], binvar=emp[t, i, j])
            # a filling pour moves exactly the room left in the target
            m.addConsIndicator(a >= caps[j] - prev[j], binvar=full[t, i, j])
            # no amount without a pour
            m.addCons(a <= cmax * p)

        # water balance of each bucket across the pour
        for k in range(K):
            outflow = quicksum(amt[t, k, j] for j in range(K) if j != k)
            inflow = quicksum(amt[t, j, k] for j in range(K) if j != k)
            m.addCons(cur[k] == prev[k] - outflow + inflow)

    # output sequence: the states from the start, then padding after the goal
    out = [
        [m.addVar(name=f"out_{t}_{k}", vtype="I", lb=pad, ub=caps[k]) for k in range(K)]
        for t in range(steps)
    ]
    for k in range(K):
        m.addCons(out[0][k] == s[0][k])
    for t in range(1, steps):
        for k in range(K):
            # goal not reached before this step: the output is the state
            m.addConsIndicator(out[t][k] - s[t][k] <= 0, binvar=done[t - 1], activeone=False)
            m.addConsIndicator(out[t][k] - s[t][k] >= 0, binvar=done[t - 1], activeone=False)
            # goal already reached: the output is the padding value
            m.addConsIndicator(out[t][k] <= pad, binvar=done[t - 1])
            m.addConsIndicator(out[t][k] >= pad, binvar=done[t - 1])

    cost = quicksum(y.values())
    m.setObjective(cost, "minimize")
    return m, {"cost": cost, "sequence": out}
