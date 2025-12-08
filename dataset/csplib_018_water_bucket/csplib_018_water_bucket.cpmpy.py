#!/usr/bin/python3
# Category: csplib
# Source description: https://www.csplib.org/Problems/prob018/
# Source model: https://www.csplib.org/Problems/prob018/models/WaterBucket.py.html

"""
You are given an 8 pint bucket of water, and two empty buckets which can contain 5 and 3 pints respectively.
You are required to divide the water into two by pouring water between buckets (that is, to end up with
4 pints in the 8 pint bucket, and 4 pints in the 5 pint bucket).

This task is to find the minimum number of transfers of water between buckets to reach the goal.

Print the minimum number of transfers (cost) and the sequence of states (sequence). The sequence must
be a list of exactly MAX_STEPS integer lists. After the goal state is reached, the remainder of the list must be
padded with the padding states, e.g. [-1, -1, -1].
"""

# Data
capacities = [8, 5, 3]
initial_state = [8, 0, 0]
goal_state = [4, 4, 0]
MAX_STEPS = 20      # The fixed length of the output sequence.
PADDING_VALUE = -1   # The value used for padding unused steps.
# End of data

import cpmpy as cp
import json
import numpy as np

# --- Pre-computation of all valid state transitions ---
# This part derives the transition logic from the rules of pouring water.
all_states = []
for i in range(capacities[0] + 1):
    for j in range(capacities[1] + 1):
        if capacities[0] - i - j >= 0 and capacities[0] - i - j <= capacities[2]:
            k = capacities[0] - i - j
            all_states.append((i, j, k))

transitions = []
for state in all_states:
    for i in range(3):
        for j in range(3):
            if i == j: continue
            current_amounts = list(state)
            pour_amount = min(current_amounts[i], capacities[j] - current_amounts[j])
            if pour_amount > 0:
                next_state = list(current_amounts)
                next_state[i] -= pour_amount
                next_state[j] += pour_amount
                transitions.append(tuple(state) + tuple(next_state))
transitions = sorted(list(set(transitions)))
# End of pre-computation

# Model definition
model = cp.Model()

# Decision Variables
# The state of the buckets at each step. The domain includes the PADDING_VALUE.
total_water = max(initial_state)
sequence = cp.intvar(PADDING_VALUE, total_water, shape=(MAX_STEPS, 3), name="states")

# Constraints
# The sequence must start with the initial state.
model += sequence[0, :] == initial_state

# Logic for state properties.
for t in range(MAX_STEPS):
    is_padded = (sequence[t, 0] == PADDING_VALUE)
    # If a state is not padded, its values must be non-negative and conserve water.
    model += (~is_padded).implies(cp.sum(sequence[t, :]) == total_water)
    # Each bucket's amount must be within its capacity.
    for b in range(3):
        model += (~is_padded).implies((sequence[t, b] >= 0) & (sequence[t, b] <= capacities[b]))

# Transition logic between steps.
for t in range(MAX_STEPS - 1):
    is_padded_t = (sequence[t, 0] == PADDING_VALUE)
    is_goal_t = (sequence[t, :] == goal_state).all()

    # Rule 1: If the current state is the goal, the next state must be the padding state.
    model += is_goal_t.implies((sequence[t + 1, :] == PADDING_VALUE).all())

    # Rule 2: If the current state is padding, the next state must also be padding.
    model += is_padded_t.implies((sequence[t + 1, :] == PADDING_VALUE).all())

    # Rule 3: If not at the goal and not padded, a valid, non-repeating transfer must occur.
    must_transfer = cp.Table(np.hstack([sequence[t, :], sequence[t + 1, :]]), transitions) & \
                    cp.any(sequence[t + 1, :] != sequence[t, :])
    model += (~is_goal_t & ~is_padded_t).implies(must_transfer)

# The goal must be reached at some point in the sequence.
model += cp.any([(sequence[t, :] == goal_state).all() for t in range(MAX_STEPS)])

# Objective
# The cost is the number of transfers, which is the number of states before padding begins, minus one.
cost = cp.sum([sequence[t, 0] != PADDING_VALUE for t in range(MAX_STEPS)]) - 1
model.minimize(cost)

model.solve()

solution = {
    "cost": int(model.objective_value()),
    "sequence": sequence.value().tolist()
}
print(json.dumps(solution))
# End of CPMpy script