# Water bucket: three buckets with given capacities hold the water in the initial state; pouring one
# bucket into another until the source is empty or the target is full is a transfer. Reach the
# goal state with as few transfers as possible. The answer is a fixed-length list of states, padded
# with the padding state once the goal has been reached.
from exact import Exact


def build(instance):
    capacities = instance["capacities"]
    initial_state = instance["initial_state"]
    goal_state = instance["goal_state"]
    max_steps = instance["MAX_STEPS"]  # fixed length of the output sequence
    padding = instance["PADDING_VALUE"]  # value filling the unused steps
    n_buckets = len(capacities)
    total_water = max(initial_state)  # as in the reference, the amount of water in the system

    # Every legal state: amounts that respect the capacities and add up to the water in the system.
    states = []
    for i in range(capacities[0] + 1):
        for j in range(capacities[1] + 1):
            k = capacities[0] - i - j
            if 0 <= k <= capacities[2] and i + j + k == total_water:
                states.append((i, j, k))

    # Legal transfers: pour bucket i into bucket j as far as possible (until i is empty or j is
    # full); a transfer that moves no water is not a transfer.
    successors = {s: set() for s in states}
    for s in states:
        for i in range(n_buckets):
            for j in range(n_buckets):
                if i == j:
                    continue
                amount = min(s[i], capacities[j] - s[j])
                if amount > 0:
                    t = list(s)
                    t[i] -= amount
                    t[j] += amount
                    successors[s].add(tuple(t))

    solver = Exact()

    # at[t][s] = 1 when step t of the sequence is state s; the extra option "pad" marks a padded
    # step. Exactly one option holds at every step.
    options = states + ["pad"]
    at = [{s: f"at_{t}_{'_'.join(map(str, s)) if s != 'pad' else 'pad'}" for s in options}
          for t in range(max_steps)]
    for t in range(max_steps):
        for s in options:
            solver.addVariable(at[t][s], 0, 1)
        solver.addConstraint([(1, at[t][s]) for s in options], True, 1, True, 1)

    # sequence[t][b] is the amount in bucket b at step t, or the padding value at a padded step.
    sequence = [[f"sequence_{t}_{b}" for b in range(n_buckets)] for t in range(max_steps)]
    for t in range(max_steps):
        for b in range(n_buckets):
            solver.addVariable(sequence[t][b], padding, max(capacities[b], padding))
            solver.addConstraint([(s[b], at[t][s]) for s in states] +
                                 [(padding, at[t]["pad"]), (-1, sequence[t][b])],
                                 True, 0, True, 0)

    # The sequence starts with the initial state.
    solver.addConstraint([(1, at[0][tuple(initial_state)])], True, 1, True, 1)

    goal = tuple(goal_state)
    for t in range(max_steps - 1):
        # Once the goal is reached, the next step is padded.
        solver.addConstraint([(1, at[t + 1]["pad"]), (-1, at[t][goal])], True, 0)
        # A padded step is followed by a padded step.
        solver.addConstraint([(1, at[t + 1]["pad"]), (-1, at[t]["pad"])], True, 0)
        # Any other state is followed by a state reached by one legal transfer.
        for s in states:
            if s != goal:
                solver.addConstraint([(1, at[t + 1][u]) for u in successors[s]] + [(-1, at[t][s])],
                                     True, 0)

    # The goal must be reached at some step.
    solver.addConstraint([(1, at[t][goal]) for t in range(max_steps)], True, 1)

    # cost = number of transfers = number of unpadded steps minus one (the initial state is not a
    # transfer). It is the quantity to minimise.
    solver.addVariable("cost", 0, max_steps - 1)
    solver.addConstraint([(1, "cost")] + [(1, at[t]["pad"]) for t in range(max_steps)],
                         True, max_steps - 1, True, max_steps - 1)

    return solver, {"cost": "cost", "sequence": sequence}, ("minimize", [(1, "cost")])
