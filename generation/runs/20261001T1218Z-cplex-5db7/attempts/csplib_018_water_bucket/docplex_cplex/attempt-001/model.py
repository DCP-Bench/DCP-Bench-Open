"""CSPLib 18, water bucket: divide the water of a full bucket by pouring between three buckets
of given capacities, reaching the goal amounts in the fewest transfers.

The plan is a sequence of MAX_STEPS states; once the goal is reached, the remaining states
are padding states with every amount equal to PADDING_VALUE.
"""
from docplex.mp.model import Model


def build(instance):
    capacities = instance["capacities"]
    initial_state = instance["initial_state"]
    goal_state = instance["goal_state"]
    max_steps = instance["MAX_STEPS"]
    pad = instance["PADDING_VALUE"]
    n_buckets = len(capacities)
    steps = range(max_steps)

    # The states the reference allows: every split (i, j, k) of capacities[0] pints with each
    # amount within its bucket's capacity, as in the reference's pre-computation.
    all_states = []
    for i in range(capacities[0] + 1):
        for j in range(capacities[1] + 1):
            k = capacities[0] - i - j
            if 0 <= k <= capacities[2]:
                all_states.append((i, j, k))
    total_water = max(initial_state)

    # The valid pourings: pour from bucket a into bucket b until a is empty or b is full,
    # moving a positive amount.
    successors = {state: set() for state in all_states}
    for state in all_states:
        for a in range(n_buckets):
            for b in range(n_buckets):
                if a == b:
                    continue
                amount = min(state[a], capacities[b] - state[b])
                if amount > 0:
                    after = list(state)
                    after[a] -= amount
                    after[b] += amount
                    successors[state].add(tuple(after))

    # A state that is not padding holds all the water, each bucket within its capacity.
    states = [s for s in all_states if sum(s) == total_water]
    start = tuple(initial_state)
    if start not in states and sum(start) == total_water and all(
            0 <= start[b] <= capacities[b] for b in range(n_buckets)):
        states.append(start)
    goal = tuple(goal_state)
    index = {s: q for q, s in enumerate(states)}
    PAD = len(states)  # index of the padding state
    options = range(len(states) + 1)

    model = Model("water_bucket")

    # at[t, q] is 1 when step t is in state q (or padding, q == PAD); one state per step.
    at = {(t, q): model.binary_var(name=f"at_{t}_{q}") for t in steps for q in options}
    for t in steps:
        model.add_constraint(model.sum(at[t, q] for q in options) == 1)

    # The sequence starts with the initial state.
    model.add_constraint(at[0, index[start]] == 1)

    for t in range(max_steps - 1):
        for s in states:
            q = index[s]
            if s == goal:
                # After the goal, the next state is padding.
                model.add_constraint(at[t, q] <= at[t + 1, PAD])
            else:
                # Otherwise a transfer happens: the next state is one valid pouring away,
                # which always changes the state.
                model.add_constraint(
                    at[t, q] <= model.sum(at[t + 1, index[n]] for n in successors.get(s, ())
                                          if n in index))
        # After padding, the next state is padding.
        model.add_constraint(at[t, PAD] <= at[t + 1, PAD])

    # The goal is reached at some step.
    model.add_constraint(model.sum(at[t, index[goal]] for t in steps) >= 1)

    # sequence[t][b] is the amount in bucket b at step t, or the padding value.
    sequence = [[model.sum(s[b] * at[t, index[s]] for s in states if s[b] != 0)
                 + pad * at[t, PAD] for b in range(n_buckets)] for t in steps]

    # The cost is the number of transfers: the number of steps before padding, minus one.
    cost = model.integer_var(0, max_steps - 1, name="cost")
    model.add_constraint(cost == model.sum(1 - at[t, PAD] for t in steps) - 1)
    model.minimize(cost)

    return model, {"cost": cost, "sequence": sequence}
