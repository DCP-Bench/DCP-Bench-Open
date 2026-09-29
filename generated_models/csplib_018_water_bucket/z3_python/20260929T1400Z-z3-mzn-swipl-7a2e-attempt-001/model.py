# Water bucket: three buckets with given capacities start in the initial state
# and water is poured from one bucket into another (until the source is empty
# or the target full). Reach the goal state with as few pourings as possible.
# The states are listed one per step in a fixed-length sequence, padded after the goal.
import z3


def build(instance):
    capacities = instance["capacities"]
    initial_state = instance["initial_state"]
    goal_state = instance["goal_state"]
    max_steps = instance["MAX_STEPS"]  # length of the output sequence
    pad = instance["PADDING_VALUE"]  # marks the unused steps after the goal
    n = len(capacities)
    total_water = sum(initial_state)  # the water is only moved around, never lost

    # every state within the capacities that holds all the water
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

    # one step of the sequence is either a pouring from a state that is not the
    # goal, a move from the goal into the padding, or padding after padding
    goal = tuple(goal_state)
    padding = (pad,) * n
    transitions = sorted({p for p in pourings if p[:n] != goal} | {goal + padding, padding + padding})

    solver = z3.Solver()

    # sequence[t] = the amounts in the buckets after t pourings, or padding
    sequence = [[z3.Int(f"sequence_{t}_{b}") for b in range(n)] for t in range(max_steps)]
    for t in range(max_steps):
        for b in range(n):
            solver.add(sequence[t][b] >= pad, sequence[t][b] <= total_water)

    # the sequence starts with the initial state
    for b in range(n):
        solver.add(sequence[0][b] == initial_state[b])

    # each step follows from the one before by a legal pouring; the goal is
    # followed by padding, and once padding starts it goes on
    for t in range(max_steps - 1):
        cells = sequence[t] + sequence[t + 1]
        solver.add(z3.Or([z3.And([cell == value for cell, value in zip(cells, row)]) for row in transitions]))
    # the last step is the goal or padding, so the goal has been reached at some point
    solver.add(z3.Or([z3.And([cell == value for cell, value in zip(sequence[max_steps - 1], row)])
                      for row in (goal, padding)]))

    # cost = number of pourings = number of states before the padding starts, minus one
    cost = z3.Int("cost")
    solver.add(cost == z3.Sum([z3.If(sequence[t][0] != pad, 1, 0) for t in range(max_steps)]) - 1)

    return solver, {"cost": cost, "sequence": sequence}, ("minimize", cost)
