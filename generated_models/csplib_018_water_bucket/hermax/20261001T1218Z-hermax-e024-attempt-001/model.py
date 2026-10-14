# Water bucket (CSPLib 18): starting from a full bucket and empty ones, pour water between
# buckets until the goal amounts are reached, in as few transfers as possible. The
# sequence of states is reported over a fixed number of steps, padded after the goal.
import functools
import operator

from hermax.model import Model


def any_of(lits):
    return functools.reduce(operator.or_, lits)


def build(instance):
    capacities = instance["capacities"]
    initial = tuple(instance["initial_state"])
    goal = tuple(instance["goal_state"])
    steps = instance["MAX_STEPS"]
    pad_value = instance["PADDING_VALUE"]
    buckets = len(capacities)
    total = sum(initial)  # pouring never adds or removes water

    # Every state the buckets can be in: each bucket within its capacity, all the water kept.
    def all_states(b, left):
        if b == buckets - 1:
            return [(left,)] if left <= capacities[b] else []
        return [(a,) + rest for a in range(min(left, capacities[b]) + 1)
                for rest in all_states(b + 1, left - a)]
    states = all_states(0, total)
    index = {s: k for k, s in enumerate(states)}

    # A transfer pours from bucket i into bucket j until i is empty or j is full, and must
    # move some water.
    successors = []
    for s in states:
        nxt = set()
        for i in range(buckets):
            for j in range(buckets):
                amount = min(s[i], capacities[j] - s[j]) if i != j else 0
                if amount > 0:
                    t = list(s)
                    t[i] -= amount
                    t[j] += amount
                    nxt.add(index[tuple(t)])
        successors.append(sorted(nxt))

    m = Model()
    # sequence[t][b] = water in bucket b at step t, or the padding value after the goal
    sequence = m.int_matrix("sequence", steps, buckets, min(pad_value, 0), max(total, pad_value))
    # cost = the number of transfers
    cost = m.int("cost", 0, steps - 1)
    # at[t][k] = at step t the buckets are in state k; pad[t] = step t is padding
    at = m.bool_matrix("at", steps, len(states))
    pad = m.bool_vector("pad", steps)

    for t in range(steps):
        # each step is exactly one state, or padding
        options = [at[t][k] for k in range(len(states))] + [pad[t]]
        m &= any_of(options)
        for a in range(len(options)):
            for b in range(a + 1, len(options)):
                m &= (~options[a] | ~options[b])
        # the reported amounts are those of the state, or the padding value
        for k, s in enumerate(states):
            for b in range(buckets):
                m &= (~at[t][k] | (sequence[t][b] == s[b]))
        for b in range(buckets):
            m &= (~pad[t] | (sequence[t][b] == pad_value))

    # the sequence starts with the initial state
    m &= at[0][index[initial]]

    goal_k = index[goal]
    for t in range(steps - 1):
        # once the goal is reached, or padding has started, the rest is padding
        m &= (~at[t][goal_k] | pad[t + 1])
        m &= (~pad[t] | pad[t + 1])
        # otherwise one transfer leads to the next state
        for k in range(len(states)):
            if k != goal_k:
                m &= any_of([~at[t][k]] + [at[t + 1][q] for q in successors[k]])

    # the goal is reached at some step
    m &= any_of([at[t][goal_k] for t in range(steps)])

    # cost = number of non-padding steps minus one. Padding is a suffix, so cost is k
    # exactly when step k is the last one that is not padding.
    for k in range(steps):
        if k + 1 < steps:
            m &= (~(cost == k) | ~pad[k])
            m &= (~(cost == k) | pad[k + 1])
            m &= (pad[k] | ~pad[k + 1] | (cost == k))
        else:
            m &= (~(cost == k) | ~pad[k])
            m &= (pad[k] | (cost == k))

    # Minimise the transfers: a soft clause pays 1 when its literal is false, so "step t is
    # padding" pays 1 for every step after the first that is not padding.
    for t in range(1, steps):
        m.obj[1] += pad[t]

    return m, {"cost": cost, "sequence": sequence}
