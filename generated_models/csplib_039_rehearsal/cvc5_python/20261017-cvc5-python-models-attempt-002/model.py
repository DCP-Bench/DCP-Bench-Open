# csplib_039_rehearsal: order the pieces of a concert so that the total time
# players spend waiting (present but not currently playing) is minimised.
# Encoding: pairwise precedence Booleans with transitivity instead of a permutation
# of integers, so the search runs on Boolean structure rather than Distinct.
from cvc5.pythonic import Bool, Int, If, Or, And, Not, Implies, Sum


def build(instance):
    n = instance["num_pieces"]
    num_players = instance["num_players"]
    dur = instance["duration"]
    rehearsal = instance["rehearsal"]

    # before(i, j): piece i is rehearsed before piece j (one Boolean per unordered pair)
    pair = {}
    for i in range(n):
        for j in range(i + 1, n):
            pair[(i, j)] = Bool(f"before_{i}_{j}")

    def before(i, j):
        return pair[(i, j)] if i < j else Not(pair[(j, i)])

    constraints = []
    # the order is transitive: if i comes before j and j before k, i comes before k
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if len({i, j, k}) == 3:
                    constraints.append(Implies(And(before(i, j), before(j, k)), before(i, k)))

    # slot of each piece = the number of pieces rehearsed before it
    pos = [Sum([If(before(i, j), 1, 0) for i in range(n) if i != j]) for j in range(n)]
    # rehearsal_order[k] is the piece rehearsed in slot k
    order = [Int(f"order_{k}") for k in range(n)]
    for k in range(n):
        constraints += [order[k] >= 0, order[k] <= n - 1]
    for j in range(n):
        for k in range(n):
            constraints.append(Implies(pos[j] == k, order[k] == j))

    # a player is present from the first piece he takes part in until the last one;
    # the time he is present but not playing is the duration of each such piece
    waiting = []
    for p in range(num_players):
        played = [i for i in range(n) if rehearsal[p][i] == 1]
        if not played:
            continue
        for j in range(n):
            if rehearsal[p][j] == 1:
                continue
            # some piece he plays comes before piece j
            starts_before = [before(i, j) for i in played]
            # some piece he plays comes after piece j
            ends_after = [before(j, i) for i in played]
            present = And(
                starts_before[0] if len(starts_before) == 1 else Or(starts_before),
                ends_after[0] if len(ends_after) == 1 else Or(ends_after),
            )
            waiting.append(If(present, dur[j], 0))

    total = Sum(waiting)
    return constraints, {"rehearsal_order": order}, ("minimize", total)
