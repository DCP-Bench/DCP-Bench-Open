from pycsp3 import *

# the rows of the sequence are the states of the three buckets, from the initial state.
# the rows after the goal state are padding; the sequence ends in padding, so the goal is
# reached within MAX_STEPS - 1 transfers.
STEPS = data.MAX_STEPS
PAD = data.PADDING_VALUE
caps = data.capacities
total = sum(data.initial_state)

sequence = VarArray(size=[STEPS, 3], dom=range(min(PAD, 0), max(caps) + 1))
# cost is the number of transfers, which is the number of states after the first one
cost = Var(dom=range(STEPS))

# every state of the buckets, with the same total water
states = [(a, b, c) for a in range(caps[0] + 1) for b in range(caps[1] + 1) for c in range(caps[2] + 1)
          if a + b + c == total]

# a transfer pours water from one bucket into another until one of them is empty or full
supports = []
for s in states:
    for i in range(3):
        for j in range(3):
            if i == j or s[i] == 0 or s[j] == caps[j]:
                continue
            amount = min(s[i], caps[j] - s[j])
            t = list(s)
            t[i] -= amount
            t[j] += amount
            supports.append(tuple(s) + tuple(t))
# the goal state is followed by padding, and padding is followed by padding
goal = tuple(data.goal_state)
supports.append(goal + (PAD, PAD, PAD))
supports.append((PAD, PAD, PAD, PAD, PAD, PAD))

satisfy(
    # the first state is the initial state
    [sequence[0][k] == data.initial_state[k] for k in range(3)],
    # each step is a transfer between buckets, or padding after the goal state
    [Table(scope=sequence[t] + sequence[t + 1], supports=supports) for t in range(STEPS - 1)],
    # the last row is padding, so the goal state is not in the last row
    [sequence[STEPS - 1][k] == PAD for k in range(3)],
    # the goal state is reached: the number of transfers counts the non-padding rows after the first
    cost == Sum(sequence[t][0] != PAD for t in range(1, STEPS)),
)

# minimise the number of transfers
minimize(cost)
