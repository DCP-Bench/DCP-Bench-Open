"""Water bucket (CSPLib 18): starting from a full large bucket and two empty smaller ones,
pour water between the buckets to reach the goal amounts with as few transfers as
possible. A pour empties the source or fills the destination, whichever comes first.

The model reports the minimum number of transfers (cost) and the sequence of states,
padded after the goal with rows of PADDING_VALUE up to MAX_STEPS rows.
"""
import pulp


def build(instance):
    capacities = instance["capacities"]
    initial_state = tuple(instance["initial_state"])
    goal_state = tuple(instance["goal_state"])
    max_steps = instance["MAX_STEPS"]
    pad = instance["PADDING_VALUE"]
    total_water = max(initial_state)  # as in the reference
    buckets = range(3)
    steps = range(max_steps)

    # The states and pours, derived from the rules exactly as the reference does: a state
    # has the first two buckets within capacity and the rest of capacities[0] in the
    # third; a pour moves as much water as fits from bucket i to bucket j.
    all_states = []
    for i in range(capacities[0] + 1):
        for j in range(capacities[1] + 1):
            k = capacities[0] - i - j
            if 0 <= k <= capacities[2]:
                all_states.append((i, j, k))
    transitions = set()
    for state in all_states:
        for i in buckets:
            for j in buckets:
                if i == j:
                    continue
                amount = min(state[i], capacities[j] - state[j])
                if amount > 0:
                    after = list(state)
                    after[i] -= amount
                    after[j] += amount
                    transitions.add((state, tuple(after)))
    transitions = sorted(transitions)

    # A row that is not padding holds water within each capacity and conserves the total.
    states = [st for st in all_states
              if sum(st) == total_water and all(0 <= st[b] <= capacities[b] for b in buckets)]
    if initial_state not in states:
        states.append(initial_state)
    transitions = [(s, t) for s, t in transitions if s in states and t in states]

    problem = pulp.LpProblem("water_bucket", pulp.LpMinimize)

    # at[t][state] = 1 if row t of the sequence is that state; a row with none is padding
    at = [{st: pulp.LpVariable(f"at_{t}_{st[0]}_{st[1]}_{st[2]}", cat="Binary") for st in states}
          for t in steps]
    for t in steps:
        problem += pulp.lpSum(at[t].values()) <= 1

    # pour[t][(s, s2)] = 1 if the transfer after row t turns state s into state s2
    pour = [{arc: pulp.LpVariable(f"pour_{t}_{arc[0][0]}{arc[0][1]}{arc[0][2]}_"
                                  f"{arc[1][0]}{arc[1][1]}{arc[1][2]}", cat="Binary")
             for arc in transitions} for t in range(max_steps - 1)]

    # the sequence starts with the initial state
    problem += at[0][initial_state] == 1

    for t in range(max_steps - 1):
        for st in states:
            leaving = pulp.lpSum(var for (s, _), var in pour[t].items() if s == st)
            if st == goal_state:
                # once the goal is reached no transfer follows: the next rows are padding
                problem += leaving == 0
            else:
                # a state that is not the goal is followed by one valid transfer
                problem += leaving == at[t][st]
        # a row after the first is a state only when a transfer led to it, so padding is
        # followed by padding and the goal by padding
        for st in states:
            problem += at[t + 1][st] == pulp.lpSum(var for (_, s2), var in pour[t].items()
                                                   if s2 == st)

    # the goal must be reached at some point in the sequence
    problem += pulp.lpSum(at[t][goal_state] for t in steps if goal_state in at[t]) >= 1

    # cost: the number of transfers, one less than the number of rows that are states
    cost = pulp.LpVariable("cost", 0, max_steps - 1, cat="Integer")
    problem += cost == pulp.lpSum(var for t in steps for var in at[t].values()) - 1
    problem += cost

    # each row: the amounts of the state it holds, or PADDING_VALUE in every bucket
    sequence = [[pulp.lpSum(st[b] * var for st, var in at[t].items())
                 + pad * (1 - pulp.lpSum(at[t].values())) for b in buckets] for t in steps]
    return problem, {"cost": cost, "sequence": sequence}
