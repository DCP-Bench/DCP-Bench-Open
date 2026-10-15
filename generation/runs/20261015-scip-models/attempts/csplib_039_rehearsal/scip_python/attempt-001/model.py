# Rehearsal ordering: order the pieces in rehearsal slots so that the total time
# players spend waiting (present at the rehearsal but not playing) is minimal.
# A player arrives just before the first piece they play and leaves just after
# the last one, so their waiting time is (departure - arrival) minus their playing time.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["num_pieces"]
    n_players = instance["num_players"]
    duration = instance["duration"]
    involved = instance["rehearsal"]  # involved[player][piece] = 1 if the player plays the piece

    total = sum(duration)

    m = Model("rehearsal")
    m.hideOutput()

    # slot[i, k] = 1 if piece i is rehearsed in slot k
    slot = {(i, k): m.addVar(name=f"slot_{i}_{k}", vtype="B") for i in range(n) for k in range(n)}

    # each piece is rehearsed in exactly one slot, and each slot holds one piece
    for i in range(n):
        m.addCons(quicksum(slot[i, k] for k in range(n)) == 1)
    for k in range(n):
        m.addCons(quicksum(slot[i, k] for i in range(n)) == 1)

    # time[k] is the start of slot k; time[n] is the end of the last slot
    time = [m.addVar(name=f"time_{k}", vtype="C", lb=0, ub=total) for k in range(n + 1)]
    m.addCons(time[0] == 0)
    m.addCons(time[n] == total)
    # slot k lasts as long as the piece rehearsed in it
    for k in range(n):
        m.addCons(time[k + 1] - time[k] == quicksum(duration[i] * slot[i, k] for i in range(n)))

    # playing time of the players, which is fixed by the data
    playing_time = sum(
        involved[j][i] * duration[i] for j in range(n_players) for i in range(n)
    )

    # arrival[j] and departure[j] bound the rehearsal time of player j.
    # Only players who play at least one piece are modelled.
    arrival = {}
    departure = {}
    for j in range(n_players):
        if sum(involved[j]) == 0:
            continue
        arrival[j] = m.addVar(name=f"arrival_{j}", vtype="C", lb=0, ub=total)
        departure[j] = m.addVar(name=f"departure_{j}", vtype="C", lb=0, ub=total)
        for i in range(n):
            if not involved[j][i]:
                continue
            for k in range(n):
                # the player arrives no later than the start of a slot with one of their pieces
                m.addConsIndicator(arrival[j] - time[k] <= 0, binvar=slot[i, k])
                # the player leaves no earlier than the end of a slot with one of their pieces
                m.addConsIndicator(time[k + 1] - departure[j] <= 0, binvar=slot[i, k])

    # waiting time = total presence of all players - total playing time
    presence = quicksum(departure[j] - arrival[j] for j in arrival)
    m.setObjective(presence - playing_time, "minimize")

    # the piece rehearsed in each slot, numbered from 0
    rehearsal_order = [quicksum(i * slot[i, k] for i in range(n)) for k in range(n)]

    outputs = {"rehearsal_order": rehearsal_order}
    return m, outputs
