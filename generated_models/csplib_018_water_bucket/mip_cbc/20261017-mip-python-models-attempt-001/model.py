# Water bucket (CSPlib 018). Three buckets with capacities given by the instance. Start with the
# first bucket full and the others empty. A transfer pours from one bucket into another until the
# source is empty or the destination is full. Find the minimum number of transfers that reach the
# goal state, and the sequence of states (padded with the padding value after the goal is reached).
import itertools

import mip


def build(instance):
    caps = instance["capacities"]
    init = tuple(instance["initial_state"])
    goal = tuple(instance["goal_state"])
    steps = instance["MAX_STEPS"]
    pad = instance["PADDING_VALUE"]
    nb = len(caps)
    total = sum(init)

    # States: every bucket filling within its capacity, and the water kept (pouring conserves it).
    states = [s for s in itertools.product(*[range(c + 1) for c in caps]) if sum(s) == total]
    index = {s: k for k, s in enumerate(states)}

    # Pours: from state s, pour from bucket i to bucket j until i is empty or j is full.
    # A pour that moves no water is not a transfer, so it is left out.
    moves = []
    for s in states:
        for i in range(nb):
            for j in range(nb):
                if i == j:
                    continue
                amount = min(s[i], caps[j] - s[j])
                if amount <= 0:
                    continue
                t_state = list(s)
                t_state[i] -= amount
                t_state[j] += amount
                moves.append((s, tuple(t_state)))

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Step t is a real transfer (a[t] = 1) or padding (a[t] = 0). Real transfers come first.
    a = [model.add_var(f"active_{t}", var_type=mip.BINARY) for t in range(steps - 1)]
    for t in range(1, steps - 1):
        model.add_constr(a[t] <= a[t - 1])

    # w[t][s] = 1 when the water is in state s after t transfers.
    w = [[model.add_var(f"w_{t}_{k}", var_type=mip.BINARY) for k in range(len(states))]
         for t in range(steps)]
    for t in range(steps):
        model.add_constr(mip.xsum(w[t]) == 1)
    model.add_constr(w[0][index[init]] == 1)
    model.add_constr(w[steps - 1][index[goal]] == 1)

    # f[t][m] = 1 when transfer t is the move m. A padded step stays in the goal state.
    f = [[model.add_var(f"f_{t}_{m}", var_type=mip.BINARY) for m in range(len(moves))]
         for t in range(steps - 1)]

    out_moves = [[] for _ in states]
    in_moves = [[] for _ in states]
    for m, (src, dst) in enumerate(moves):
        out_moves[index[src]].append(m)
        in_moves[index[dst]].append(m)

    for t in range(steps - 1):
        # Exactly one move in an active step, none in a padded step.
        model.add_constr(mip.xsum(f[t]) == a[t])
        stay = 1 - a[t]
        for k, s in enumerate(states):
            # Leaving state s at step t: a move, or staying when s is the goal.
            leave = [f[t][m] for m in out_moves[k]]
            if s == goal:
                model.add_constr(w[t][k] == mip.xsum(leave) + stay)
            else:
                model.add_constr(w[t][k] == mip.xsum(leave))
            # Entering state s at step t + 1: a move, or staying when s is the goal.
            enter = [f[t][m] for m in in_moves[k]]
            if s == goal:
                model.add_constr(w[t + 1][k] == mip.xsum(enter) + stay)
            else:
                model.add_constr(w[t + 1][k] == mip.xsum(enter))

    # Output: the state after t transfers, and the padding value after the goal is reached.
    # Row 0 is the initial state. Row t (t >= 1) equals the state when transfer t-1 is real,
    # and the padding value otherwise.
    sequence = [list(init)]
    for t in range(1, steps):
        row = []
        act = a[t - 1]
        for i in range(nb):
            base = mip.xsum(s[i] * w[t][k] for k, s in enumerate(states) if s[i] != 0)
            y = model.add_var(f"y_{t}_{i}", lb=pad, ub=caps[i], var_type=mip.INTEGER)
            model.add_constr(y - base <= (caps[i] - pad) * (1 - act))
            model.add_constr(base - y <= (caps[i] - pad) * (1 - act))
            model.add_constr(y <= caps[i] * act + pad * (1 - act))
            row.append(y)
        sequence.append(row)

    cost = mip.xsum(f[t][m] for t in range(steps - 1) for m in range(len(moves)))
    model.objective = cost
    return model, {"cost": cost, "sequence": sequence}
