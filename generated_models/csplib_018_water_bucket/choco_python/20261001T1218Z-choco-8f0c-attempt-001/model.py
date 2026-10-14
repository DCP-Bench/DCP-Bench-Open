# Water bucket problem (CSPLib 18): starting from the initial contents of three buckets, pour water
# between them (each pour empties the source or fills the target) to reach the goal contents in as
# few transfers as possible. The sequence of states has a fixed length; after the goal it is padded.
from pychoco.model import Model


def build(instance):
    capacities = instance["capacities"]
    initial_state = instance["initial_state"]
    goal_state = instance["goal_state"]
    max_steps = instance["MAX_STEPS"]  # fixed length of the state sequence
    pad = instance["PADDING_VALUE"]  # value filling the states after the goal
    n_buckets = len(capacities)
    total_water = max(initial_state)  # as in the reference: the water in the full bucket

    # Every state the buckets can be in: each bucket within its capacity, all water kept.
    states = []

    def enumerate_states(prefix):
        if len(prefix) == n_buckets:
            if sum(prefix) == total_water:
                states.append(tuple(prefix))
            return
        for amount in range(capacities[len(prefix)] + 1):
            enumerate_states(prefix + [amount])

    enumerate_states([])
    index = {s: k for k, s in enumerate(states)}
    pad_index = len(states)  # the padding state gets the index after the real states
    goal_index = index[tuple(goal_state)]

    # Allowed (state, next state) pairs, by index. From a state that is not the goal, one pour from
    # bucket i into bucket j of min(contents of i, room left in j) > 0 pints. After the goal, and
    # after padding, comes padding.
    moves = set()
    for s in states:
        if index[s] == goal_index:
            continue
        for i in range(n_buckets):
            for j in range(n_buckets):
                if i == j:
                    continue
                amount = min(s[i], capacities[j] - s[j])
                if amount > 0:
                    nxt = list(s)
                    nxt[i] -= amount
                    nxt[j] += amount
                    moves.add((index[s], index[tuple(nxt)]))
    moves.add((goal_index, pad_index))
    moves.add((pad_index, pad_index))

    model = Model()

    # state[t] = index of the state at step t (pad_index once the goal has been passed)
    state = [model.intvar(0, pad_index, name=f"state_{t}") for t in range(max_steps)]
    # sequence[t][b] = pints in bucket b at step t, or the padding value
    sequence = [[model.intvar(min(pad, 0), max(max(capacities), pad), name=f"sequence_{t}_{b}")
                 for b in range(n_buckets)] for t in range(max_steps)]
    contents = [(k,) + s for k, s in enumerate(states)] + [(pad_index,) + (pad,) * n_buckets]
    for t in range(max_steps):
        model.table([state[t]] + sequence[t], contents).post()

    # The sequence starts with the initial state.
    model.arithm(state[0], "=", index[tuple(initial_state)]).post()

    # Each step is a valid transfer, or the padding after the goal.
    for t in range(max_steps - 1):
        model.table([state[t], state[t + 1]], [list(mv) for mv in moves]).post()

    # The goal is reached: since padding only follows the goal, the last state is the goal or padding.
    model.member(state[max_steps - 1], [goal_index, pad_index]).post()

    # The cost is the number of transfers: the number of states before the padding, minus one.
    n_pad = model.intvar(0, max_steps, name="n_pad")
    model.count(pad_index, state, n_pad).post()
    cost = model.intvar(0, max_steps - 1, name="cost")
    model.arithm(cost, "+", n_pad, "=", max_steps - 1).post()

    return model, {"cost": cost, "sequence": sequence}, ("minimize", cost)
