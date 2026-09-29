# Water bucket: three buckets with given capacities start in the initial state
# and water is poured from one bucket into another (until the source is empty
# or the target full). Reach the goal state with as few pourings as possible.
# The states are listed one per step in a fixed-length sequence, padded after the goal.
from ortools.sat.python import cp_model


def build(instance):
    capacities = instance["capacities"]
    initial_state = instance["initial_state"]
    goal_state = instance["goal_state"]
    max_steps = instance["MAX_STEPS"]  # length of the output sequence
    pad = instance["PADDING_VALUE"]  # marks the unused steps after the goal
    n = len(capacities)
    total_water = sum(initial_state)  # the water is only moved around, never lost

    # every reachable-by-rule state: buckets within capacity holding all the water
    states = [
        (i, j, total_water - i - j)
        for i in range(capacities[0] + 1)
        for j in range(capacities[1] + 1)
        if 0 <= total_water - i - j <= capacities[2]
    ]
    # every legal pouring, as (state before, state after) tuples
    pourings = set()
    for state in states:
        for src in range(n):
            for dst in range(n):
                if src == dst:
                    continue
                amount = min(state[src], capacities[dst] - state[dst])  # pour until empty or full
                if amount > 0:
                    after = list(state)
                    after[src] -= amount
                    after[dst] += amount
                    pourings.add(tuple(state) + tuple(after))

    # one step of the sequence is either a pouring, a move from the goal into
    # the padding, or padding after padding; the goal is the only way to stop
    goal = tuple(goal_state)
    padding = (pad,) * n
    transitions = {p for p in pourings if p[:n] != goal}
    transitions.add(goal + padding)
    transitions.add(padding + padding)
    transitions = sorted(transitions)

    model = cp_model.CpModel()

    # sequence[t] = the amounts in the buckets after t pourings, or padding
    sequence = [[model.new_int_var(pad, total_water, f"sequence_{t}_{b}") for b in range(n)] for t in range(max_steps)]

    # the sequence starts with the initial state
    for b in range(n):
        model.add(sequence[0][b] == initial_state[b])

    # each step follows from the one before by a legal pouring; the goal is
    # followed by padding, and once padding starts it goes on
    for t in range(max_steps - 1):
        model.add_allowed_assignments(sequence[t] + sequence[t + 1], transitions)
    # the last step is the goal or padding, so the goal has been reached at some point
    model.add_allowed_assignments(sequence[max_steps - 1], [goal, padding])

    # cost = number of pourings = number of states before the padding starts, minus one
    used = []
    for t in range(max_steps):
        flag = model.new_bool_var(f"used_{t}")
        model.add(sequence[t][0] != pad).only_enforce_if(flag)
        model.add(sequence[t][0] == pad).only_enforce_if(flag.negated())
        used.append(flag)
    cost = model.new_int_var(0, max_steps - 1, "cost")
    model.add(cost == sum(used) - 1)
    model.minimize(cost)

    return model, {"cost": cost, "sequence": sequence}
