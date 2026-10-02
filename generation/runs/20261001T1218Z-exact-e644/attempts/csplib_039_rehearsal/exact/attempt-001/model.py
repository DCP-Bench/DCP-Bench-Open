# The rehearsal problem: put the pieces of a concert in a rehearsal order so that the total time
# players spend present but not playing is minimal. A player arrives just before the first piece
# they play in and leaves just after the last one.
from exact import Exact


def build(instance):
    n = instance["num_pieces"]
    players = instance["num_players"]
    duration = instance["duration"]
    rehearsal = instance["rehearsal"]  # rehearsal[p][i] = 1 when player p plays in piece i
    total_time = sum(duration)  # every start, arrival and departure time lies in 0..total_time

    solver = Exact()

    # at_slot[i][s] = 1 when piece i is rehearsed in slot s. A permutation matrix is how Exact,
    # which has no all-different constraint, says that the order is a permutation.
    at_slot = [[f"piece_{i}_in_slot_{s}" for s in range(n)] for i in range(n)]
    for i in range(n):
        for s in range(n):
            solver.addVariable(at_slot[i][s], 0, 1)
    for i in range(n):
        # each piece is rehearsed exactly once
        solver.addConstraint([(1, at_slot[i][s]) for s in range(n)], True, 1, True, 1)
    for s in range(n):
        # each slot rehearses exactly one piece
        solver.addConstraint([(1, at_slot[i][s]) for i in range(n)], True, 1, True, 1)

    # rehearsal_order[s] is the piece rehearsed in slot s
    rehearsal_order = [f"rehearsal_order_{s}" for s in range(n)]
    for s in range(n):
        solver.addVariable(rehearsal_order[s], 0, n - 1)
        solver.addConstraint([(i, at_slot[i][s]) for i in range(1, n)] + [(-1, rehearsal_order[s])],
                             True, 0, True, 0)

    # slot_of[i] is the slot in which piece i is rehearsed
    slot_of = [f"slot_of_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(slot_of[i], 0, n - 1)
        solver.addConstraint([(s, at_slot[i][s]) for s in range(1, n)] + [(-1, slot_of[i])],
                             True, 0, True, 0)

    # before[i][j] = 1 (i < j) when piece i is rehearsed earlier than piece j. The slots differ,
    # so "not before" means that j is earlier than i.
    before = {}
    for i in range(n):
        for j in range(i + 1, n):
            before[i, j] = f"piece_{i}_before_{j}"
            solver.addVariable(before[i, j], 0, 1)
            solver.addReification(before[i, j], True, [(1, slot_of[j]), (-1, slot_of[i])], 1)

    # start[i] is the time at which piece i begins: the total duration of the pieces rehearsed
    # before it. Durations are constants, so this is linear in the before indicators:
    #   j < i is before i when before[j,i] = 1;  j > i is before i when before[i,j] = 0.
    start = [f"start_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(start[i], 0, total_time)
        terms = [(1, start[i])]
        terms += [(-duration[j], before[j, i]) for j in range(i)]
        terms += [(duration[j], before[i, j]) for j in range(i + 1, n)]
        later = sum(duration[i + 1:])  # the 1 - before[i,j] of each later piece contributes this
        solver.addConstraint(terms, True, later, True, later)

    # arrival[p] is when player p arrives, departure[p] when they leave. A player must be present
    # during every piece they play in, so arrival is at most the start of each of their pieces and
    # departure at least its end; the objective makes both as tight as possible.
    arrival = [f"arrival_{p}" for p in range(players)]
    departure = [f"departure_{p}" for p in range(players)]
    for p in range(players):
        solver.addVariable(arrival[p], 0, total_time)
        solver.addVariable(departure[p], 0, total_time)
        for i in range(n):
            if rehearsal[p][i]:
                solver.addConstraint([(1, start[i]), (-1, arrival[p])], True, 0)
                solver.addConstraint([(1, departure[p]), (-1, start[i])], True, duration[i])

    # Waiting time of player p = (departure - arrival) - the time spent playing. The playing time
    # is a constant, so minimising total waiting time is minimising the sum of presence times of
    # the players who play at all (a player in no piece is never present and costs nothing).
    objective = []
    for p in range(players):
        if any(rehearsal[p]):
            objective.append((1, departure[p]))
            objective.append((-1, arrival[p]))

    return solver, {"rehearsal_order": rehearsal_order}, ("minimize", objective)
