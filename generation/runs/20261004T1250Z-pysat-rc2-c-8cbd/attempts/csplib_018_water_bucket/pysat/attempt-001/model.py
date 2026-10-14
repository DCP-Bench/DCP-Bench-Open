# Water bucket problem (CSPLib 018): starting from the initial amounts in
# three buckets, pour water from one bucket into another (until the source is
# empty or the target is full) to reach the goal amounts in as few transfers
# as possible. The plan is a sequence of MAX_STEPS states; after the goal is
# reached the rest of the sequence holds padding states.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer


def build(instance):
    capacities = instance["capacities"]
    initial_state = instance["initial_state"]
    goal_state = instance["goal_state"]
    max_steps = instance["MAX_STEPS"]
    pad = instance["PADDING_VALUE"]
    total_water = max(initial_state)

    # The states the buckets can be in, as the reference derives them: the
    # third bucket holds whatever the first two leave of capacities[0]. A
    # state that is not padding also conserves the water and respects every
    # capacity. The initial state is a state of the plan too.
    states = []
    for i in range(capacities[0] + 1):
        for j in range(capacities[1] + 1):
            k = capacities[0] - i - j
            if 0 <= k <= capacities[2]:
                states.append((i, j, k))
    if tuple(initial_state) not in states:
        states.append(tuple(initial_state))
    states = [s for s in states
              if sum(s) == total_water and all(0 <= s[b] <= capacities[b] for b in range(3))]
    index = {s: q for q, s in enumerate(states)}

    # One transfer: pour from bucket a into bucket b until a is empty or b is
    # full; only pours that move some water count.
    moves = {q: set() for q in range(len(states))}
    for s in states:
        for a in range(3):
            for b in range(3):
                if a == b:
                    continue
                amount = min(s[a], capacities[b] - s[b])
                if amount > 0:
                    nxt = list(s)
                    nxt[a] -= amount
                    nxt[b] += amount
                    if tuple(nxt) in index:
                        moves[index[s]].add(index[tuple(nxt)])
    goal = index.get(tuple(goal_state))

    pool = IDPool()
    formula = WCNF()

    # at[t][q] is true when step t is in state q; padded[t] when step t is a
    # padding step. Each step is exactly one of these.
    at = [[pool.id(("at", t, q)) for q in range(len(states))] for t in range(max_steps)]
    padded = [pool.id(("padded", t)) for t in range(max_steps)]
    for t in range(max_steps):
        formula.extend(CardEnc.equals(lits=at[t] + [padded[t]], bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    # The sequence starts in the initial state.
    start = index.get(tuple(initial_state))
    if start is None:
        formula.append([padded[0]])
        formula.append([-padded[0]])
    else:
        formula.append([at[0][start]])

    for t in range(max_steps - 1):
        # After the goal, and after padding, comes padding.
        if goal is not None:
            formula.append([-at[t][goal], padded[t + 1]])
        formula.append([-padded[t], padded[t + 1]])
        # Any other state is followed by the result of one transfer.
        for q in range(len(states)):
            if q != goal:
                formula.append([-at[t][q]] + [at[t + 1][r] for r in sorted(moves[q])])

    # The goal is reached at some step (impossible if it is not a state).
    if goal is not None:
        formula.append([at[t][goal] for t in range(max_steps)])
    else:
        formula.append([padded[0]])
        formula.append([-padded[0]])

    # sequence[t][b], the declared output: the amount in bucket b at step t,
    # or the padding value on a padding step. Direct encoding over the
    # reference's domain PADDING_VALUE..total water.
    low, high = min(pad, 0), max(total_water, pad)
    sequence = [[Integer(f"sequence_{t}_{b}", low, high, vpool=pool) for b in range(3)]
                for t in range(max_steps)]
    for t in range(max_steps):
        for b in range(3):
            var = sequence[t][b]
            formula.extend(var.domain_clauses())
            for q, s in enumerate(states):
                formula.append([-at[t][q], var.equals(s[b])])
            formula.append([-padded[t], var.equals(pad)])

    # cost, the declared output: the number of transfers, which is the number
    # of steps before the padding starts, minus one. Padding runs to the end
    # once it starts, so cost >= t exactly when step t is not padding.
    cost = Integer("cost", 0, max(max_steps - 1, 1), encoding="coupled", vpool=pool)
    formula.extend(cost.domain_clauses())
    for t in range(1, cost.ub + 1):
        if t < max_steps:
            formula.append([-cost.ge(t), -padded[t]])
            formula.append([cost.ge(t), padded[t]])
        else:
            formula.append([-cost.ge(t)])

    # Minimise the transfers: every step after the first that is not padding
    # pays 1.
    for t in range(1, max_steps):
        formula.append([padded[t]], weight=1)

    return formula, {"cost": cost, "sequence": sequence}
