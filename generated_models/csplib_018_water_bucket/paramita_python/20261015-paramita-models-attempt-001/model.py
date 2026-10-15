# Water buckets: three buckets with capacities 8, 5 and 3 pints. Starting with
# 8 pints in the largest bucket, divide the water into two halves of 4 pints
# (4 in the 8-pint bucket, 4 in the 5-pint bucket) by pouring between buckets.
# Find the minimum number of transfers (cost) and the sequence of states.
# Model: one step per state (MAX_STEPS states, step 0 is the initial state).
# Each step holds the amount in every bucket as a one-hot choice over its
# values, plus the padding value once the goal has been reached.
from paramita.modelling import Bool, And, Or, If, Iff


def build(instance):
    cap = instance["capacities"]          # bucket capacities (pints)
    init = instance["initial_state"]      # starting amounts
    goal = instance["goal_state"]         # required amounts
    steps = instance["MAX_STEPS"]         # number of states in the sequence
    pad = instance["PADDING_VALUE"]       # value written after the goal
    nb = len(cap)

    # Values each bucket can hold at step 0 (no padding) and later (with padding).
    dom0 = [list(range(0, cap[i] + 1)) for i in range(nb)]
    domt = [[pad] + dom0[i] for i in range(nb)]

    # Amount in bucket i at step t is one-hot: xv[t][i][v].
    xv = [[{v: Bool(f"x_{t}_{i}_{v}") for v in (dom0[i] if t == 0 else domt[i])}
           for i in range(nb)] for t in range(steps)]

    cons = []
    # every bucket holds exactly one amount at every step
    for t in range(steps):
        for i in range(nb):
            cons.append(sum(xv[t][i].values()) == 1)

    # the first state is the initial state
    for i in range(nb):
        cons.append(xv[0][i][init[i]])

    # done[t]: the goal state has been reached at some step <= t
    # at_goal[t]: the state at step t is the goal state
    done = [Bool(f"done_{t}") for t in range(steps)]
    at_goal = [Bool(f"at_goal_{t}") for t in range(steps)]
    for t in range(steps):
        cons.append(Iff(at_goal[t], And([xv[t][i][goal[i]] for i in range(nb)])))
        if t == 0:
            cons.append(Iff(done[0], at_goal[0]))
        else:
            cons.append(Iff(done[t], Or([done[t - 1], at_goal[t]])))

    # the goal must be reached within MAX_STEPS states
    cons.append(done[steps - 1])

    # after the goal is reached, every bucket shows the padding value
    tr = [[{} for _ in range(nb)] for _ in range(steps)]
    for t in range(1, steps):
        for i in range(nb):
            cons.append(Iff(xv[t][i][pad], done[t - 1]))

        # each step before the goal is exactly one pour from bucket i to bucket j;
        # after the goal there is no pour
        pours = []
        for i in range(nb):
            for j in range(nb):
                if i != j:
                    tr[t][i][j] = Bool(f"pour_{t}_{i}_{j}")
                    pours.append(tr[t][i][j])
        cons.append(sum(pours) + done[t - 1] == 1)

        # a pour from i to j of m = min(source, capacity_j - target) pints:
        # source loses m, target gains m, the third bucket keeps its amount
        for i in range(nb):
            for j in range(nb):
                if i == j:
                    continue
                k = 3 - i - j                       # the third bucket
                for p in dom0[i]:
                    for q in dom0[j]:
                        m = min(p, cap[j] - q)
                        cons.append(If(And([tr[t][i][j], xv[t - 1][i][p], xv[t - 1][j][q]]),
                                       And([xv[t][i][p - m], xv[t][j][q + m]])))
                for r in dom0[k]:
                    cons.append(If(And([tr[t][i][j], xv[t - 1][k][r]]), xv[t][k][r]))

    # cost: the number of pours (every pour is one transfer)
    cost = sum(tr[t][i][j] for t in range(1, steps) for i in range(nb) for j in range(nb) if i != j)

    # sequence: amount per bucket at each step; padding value is a plain integer term
    sequence = [[sum(v * xv[t][i][v] for v in xv[t][i]) for i in range(nb)]
                for t in range(steps)]

    return cons, {"cost": cost, "sequence": sequence}, ("minimize", cost)
