"""Rehearsal problem: a concert has several pieces of different durations, each played by
a given set of the orchestra's players. A player arrives just before the first piece they
play in and leaves just after the last. Find the order in which to rehearse the pieces so
that the total time players spend waiting (present but not playing) is as small as possible.

The model reports the piece rehearsed in each slot.
"""
import pulp


def build(instance):
    n = instance["num_pieces"]
    num_players = instance["num_players"]
    duration = instance["duration"]  # duration[i] = length of piece i
    plays = instance["rehearsal"]  # plays[p][i] = 1 if player p plays in piece i

    problem = pulp.LpProblem("rehearsal", pulp.LpMinimize)

    # pos[i][t] = 1 if piece i is rehearsed in slot t. Each slot holds one piece and each
    # piece is rehearsed once, so the slots form a permutation of the pieces.
    pos = [[pulp.LpVariable(f"pos_{i}_{t}", cat="Binary") for t in range(n)] for i in range(n)]
    for i in range(n):
        problem += pulp.lpSum(pos[i]) == 1
    for t in range(n):
        problem += pulp.lpSum(pos[i][t] for i in range(n)) == 1
    # rehearsal_order[t] = the piece in slot t
    rehearsal_order = [pulp.lpSum(i * pos[i][t] for i in range(n)) for t in range(n)]

    # before[j][i] = 1 if piece j is rehearsed before piece i. A piece's slot is the
    # number of pieces before it; since the slots are 0..n-1, all different, this makes
    # `before` the order of the slots (a tournament with the scores 0..n-1 is transitive).
    before = {(j, i): pulp.LpVariable(f"before_{j}_{i}", cat="Binary")
              for i in range(n) for j in range(n) if i != j}
    for i in range(n):
        for j in range(i + 1, n):
            problem += before[(i, j)] + before[(j, i)] == 1
        problem += pulp.lpSum(t * pos[i][t] for t in range(n)) == pulp.lpSum(
            before[(j, i)] for j in range(n) if j != i)

    # start[i] = time at which piece i starts: the total length of the pieces before it
    start = [pulp.lpSum(duration[j] * before[(j, i)] for j in range(n) if j != i)
             for i in range(n)]

    # A player is present from the start of their first piece to the end of their last
    # piece. arrival[p] is no later than the start of every piece p plays, and
    # departure[p] is no earlier than the end of every piece p plays; minimising the
    # objective pulls them onto the first start and the last end.
    horizon = sum(duration)
    cost_terms = []
    fixed_playing_time = 0
    for p in range(num_players):
        pieces = [i for i in range(n) if plays[p][i] == 1]
        if not pieces:
            continue  # a player who plays nothing never waits
        arrival = pulp.LpVariable(f"arrival_{p}", 0, horizon, cat="Continuous")
        departure = pulp.LpVariable(f"departure_{p}", 0, horizon, cat="Continuous")
        for i in pieces:
            problem += arrival <= start[i]
            problem += departure >= start[i] + duration[i]
        cost_terms.append(departure - arrival)
        fixed_playing_time += sum(duration[i] for i in pieces)

    # objective: total waiting time = time present minus time playing, for each player
    problem += pulp.lpSum(cost_terms) - fixed_playing_time

    return problem, {"rehearsal_order": rehearsal_order}
