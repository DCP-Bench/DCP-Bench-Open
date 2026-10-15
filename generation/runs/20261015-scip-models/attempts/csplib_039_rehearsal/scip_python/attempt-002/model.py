# Rehearsal ordering: order the pieces so that the total time players spend
# waiting (present in the hall but not playing) is minimal.
from pyscipopt import Model, quicksum


def build(instance):
    P = instance["num_pieces"]
    M = instance["num_players"]
    dur = instance["duration"]
    plays = instance["rehearsal"]  # plays[j][i] = 1 if player j plays piece i
    T = sum(dur)  # total length of the concert, an upper bound on every time

    m = Model()

    # start[i] = time at which piece i starts
    start = {i: m.addVar(name=f"start[{i}]", vtype="C", lb=0, ub=T - dur[i]) for i in range(P)}

    # before[i, k] = 1 if piece i is rehearsed before piece k (i < k)
    before = {}
    for i in range(P):
        for k in range(i + 1, P):
            before[i, k] = m.addVar(name=f"before[{i},{k}]", vtype="B")

    def precedes(i, k):
        # expression for "piece i is rehearsed before piece k", for i != k
        return before[i, k] if i < k else 1 - before[k, i]

    # pieces do not overlap: the piece rehearsed first ends before the next one starts
    for i in range(P):
        for k in range(i + 1, P):
            # the pieces are rehearsed one after the other, in the order given by before[i, k]
            m.addConsIndicator(start[i] + dur[i] <= start[k], binvar=before[i, k])
            m.addConsIndicator(start[k] + dur[k] <= start[i], binvar=before[i, k], activeone=False)

    # slot[i, s] = 1 if piece i is the s-th piece rehearsed
    slot = {(i, s): m.addVar(name=f"slot[{i},{s}]", vtype="B") for i in range(P) for s in range(P)}
    for i in range(P):
        # each piece occupies exactly one slot
        m.addCons(quicksum(slot[i, s] for s in range(P)) == 1)
        # its slot number is the number of pieces rehearsed before it
        m.addCons(quicksum(s * slot[i, s] for s in range(P))
                  == quicksum(precedes(j, i) for j in range(P) if j != i))
    for s in range(P):
        # each slot holds exactly one piece
        m.addCons(quicksum(slot[i, s] for i in range(P)) == 1)

    # waiting time of each player: from the start of the first piece he or she plays
    # to the end of the last one, minus the time spent playing
    waiting = []
    for j in range(M):
        played = [i for i in range(P) if plays[j][i] == 1]
        if not played:
            continue  # a player who plays nothing never arrives
        arrive = m.addVar(name=f"arrive[{j}]", vtype="C", lb=0, ub=T)
        depart = m.addVar(name=f"depart[{j}]", vtype="C", lb=0, ub=T)
        # arrive is no later than the start of each piece the player plays
        for i in played:
            m.addCons(arrive <= start[i])
        # depart is no earlier than the end of each piece the player plays
        for i in played:
            m.addCons(depart >= start[i] + dur[i])
        playing_time = sum(dur[i] for i in played)
        waiting.append(depart - arrive - playing_time)

    # minimise the total waiting time
    m.setObjective(quicksum(waiting), "minimize")

    # rehearsal_order[s] = the piece rehearsed in slot s
    order = [quicksum(i * slot[i, s] for i in range(P)) for s in range(P)]
    return m, {"rehearsal_order": order}
