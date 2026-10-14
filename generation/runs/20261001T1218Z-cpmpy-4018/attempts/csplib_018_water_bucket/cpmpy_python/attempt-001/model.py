# CSPLib prob018, water bucket: three buckets with given capacities, the first full of water at the
# start. Pour water between buckets (each pour empties the source or fills the target) to reach the
# goal amounts with the fewest transfers. The state sequence is padded to a fixed length.
import cpmpy as cp


def build(instance):
    capacities = instance["capacities"]
    initial_state = instance["initial_state"]
    goal_state = instance["goal_state"]
    max_steps = instance["MAX_STEPS"]  # fixed length of the output sequence
    pad = instance["PADDING_VALUE"]  # value that fills the unused steps after the goal
    n_buckets = len(capacities)

    # Water is never created or lost: every state holds this much in total.
    total_water = sum(initial_state)

    # All states (a, b, c) that fit in the buckets and hold the total amount of water.
    all_states = [(a, b, total_water - a - b)
                  for a in range(capacities[0] + 1)
                  for b in range(capacities[1] + 1)
                  if 0 <= total_water - a - b <= capacities[2]]

    # All legal pours as rows (state before + state after). Pouring from bucket i into bucket j
    # moves min(water in i, free room in j); a pour that moves nothing is not a transfer.
    transitions = set()
    for state in all_states:
        for i in range(n_buckets):
            for j in range(n_buckets):
                if i == j:
                    continue
                amount = min(state[i], capacities[j] - state[j])
                if amount > 0:
                    nxt = list(state)
                    nxt[i] -= amount
                    nxt[j] += amount
                    transitions.add(tuple(state) + tuple(nxt))
    transitions = sorted(transitions)

    # sequence[t] = amount of water in each bucket at step t; a padding state is all `pad`.
    sequence = cp.intvar(pad, total_water, shape=(max_steps, n_buckets), name="sequence")

    model = cp.Model()

    # The sequence starts in the initial state.
    model += sequence[0] == initial_state

    for t in range(max_steps):
        padded = sequence[t, 0] == pad
        # A state that is not padding conserves the water and respects each bucket's capacity.
        model += (~padded).implies(cp.sum(sequence[t]) == total_water)
        for b in range(n_buckets):
            model += (~padded).implies((sequence[t, b] >= 0) & (sequence[t, b] <= capacities[b]))

    for t in range(max_steps - 1):
        padded = sequence[t, 0] == pad
        at_goal = cp.all(sequence[t] == goal_state)
        # Once the goal is reached, every later state is padding.
        model += at_goal.implies(cp.all(sequence[t + 1] == pad))
        # Padding stays padding.
        model += padded.implies(cp.all(sequence[t + 1] == pad))
        # Before the goal is reached, each step is one legal pour (it always changes the state,
        # because the transition table holds only pours that move water).
        step = cp.Table(list(sequence[t]) + list(sequence[t + 1]), transitions)
        model += (~at_goal & ~padded).implies(step)

    # The goal is reached at some step.
    model += cp.any([cp.all(sequence[t] == goal_state) for t in range(max_steps)])

    # cost = number of transfers = number of non-padding states minus the initial one.
    cost = cp.intvar(0, max_steps - 1, name="cost")
    model += cost == cp.sum([sequence[t, 0] != pad for t in range(max_steps)]) - 1

    # Minimise the number of transfers.
    model.minimize(cost)

    return model, {"cost": cost, "sequence": sequence}
