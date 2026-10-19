# csplib_018_water_bucket: water bucket puzzle, cvc5 (Python) model.
#
# An 8 pint bucket is full of water; the other two buckets, of 5 and 3 pints, are empty.
# Water is divided into two by pouring water between buckets, so that there are
# 4 pints in the 8 pint bucket and 4 pints in the 5 pint bucket.
# Find the minimum number of transfers of water between buckets to reach the goal.
#
# A transfer pours from one bucket into another until the source is empty or the
# destination is full. State 0 is the initial state; states 1..cost are the states after
# each transfer; the states after the goal are padded with PADDING_VALUE.

import cvc5.pythonic as cz


def build(instance):
    cap = instance["capacities"]
    init = instance["initial_state"]
    goal = instance["goal_state"]
    max_steps = instance["MAX_STEPS"]
    pad = instance["PADDING_VALUE"]
    nb = len(cap)

    cost = cz.Int("cost")
    # state[k][b]: water in bucket b after k transfers
    state = [[cz.Int(f"s_{k}_{b}") for b in range(nb)] for k in range(max_steps)]

    constraints = [cost >= 0, cost <= max_steps - 1]

    # The initial state is the one given by the instance.
    constraints += [state[0][b] == init[b] for b in range(nb)]

    # Each transfer from bucket i to bucket j pours as much as the destination can take.
    def pour(prev, nxt, i, j):
        room = cap[j] - prev[j]
        amount = cz.If(prev[i] <= room, prev[i], room)
        others = [l for l in range(nb) if l != i and l != j]
        return cz.And(
            nxt[i] == prev[i] - amount,
            nxt[j] == prev[j] + amount,
            *[nxt[l] == prev[l] for l in others],
        )

    # The states 1..cost are each the result of one transfer.
    for k in range(1, max_steps):
        moves = [
            pour(state[k - 1], state[k], i, j)
            for i in range(nb)
            for j in range(nb)
            if i != j
        ]
        constraints.append(cz.Implies(k <= cost, cz.Or(*moves)))

    # The states after the cost are padded.
    for k in range(1, max_steps):
        constraints.append(
            cz.Implies(cost < k, cz.And(*[state[k][b] == pad for b in range(nb)]))
        )

    # The state at index cost is the goal state.
    for c in range(max_steps):
        constraints.append(
            cz.Implies(cost == c, cz.And(*[state[c][b] == goal[b] for b in range(nb)]))
        )

    outputs = {
        "cost": cost,
        "sequence": [[state[k][b] for b in range(nb)] for k in range(max_steps)],
    }
    return constraints, outputs, ("minimize", cost)
