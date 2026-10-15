"""Concert rehearsal order: order the pieces so the total waiting time of the players is minimal.

Encoding: pos[j][s] is a one-hot Bool (piece j is rehearsed in slot s). Each player is present
from the slot of their first piece to the slot of their last one; waiting is presence without
playing. Durations and the player/piece matrix come from the instance.
"""
from paramita.modelling import Bool, Iff, Or


def _or(xs):
    # a one-operand Or is rejected by paramita, so a single operand is used as it is
    return xs[0] if len(xs) == 1 else Or(xs)


def build(instance):
    num_pieces = instance["num_pieces"]
    num_players = instance["num_players"]
    duration = instance["duration"]  # duration[j] of piece j
    rehearsal = instance["rehearsal"]  # rehearsal[p][j] = 1 if player p plays in piece j
    n, m = num_pieces, num_players
    slots = range(n)

    # piece j is rehearsed in slot s
    pos = [[Bool(f"piece_{j}_slot_{s}") for s in slots] for j in range(n)]

    cons = []

    # each piece is rehearsed in exactly one slot
    for j in range(n):
        cons.append(sum(pos[j][s] for s in slots) == 1)

    # each slot rehearses exactly one piece
    for s in slots:
        cons.append(sum(pos[j][s] for j in range(n)) == 1)

    waiting_terms = []  # (p, s) bool: player p is present but not playing in slot s
    waiting = [[None] * n for _ in range(m)]
    slot_wait = []  # per (p, s): (waiting bool, [piece bools]) for the objective

    for p in range(m):
        pieces = [j for j in range(n) if rehearsal[p][j]]

        # plays[s]: player p plays in slot s
        plays = []
        for s in slots:
            pl = Bool(f"plays_{p}_{s}")
            if pieces:
                cons.append(Iff(pl, _or([pos[j][s] for j in pieces])))
            else:
                cons.append(~pl)
            plays.append(pl)

        # player p arrives immediately before the first piece in which they are involved
        # started[s]: player p has arrived by slot s
        started = []
        for s in slots:
            st = Bool(f"started_{p}_{s}")
            prev = plays[s] if s == 0 else (started[s - 1] | plays[s])
            cons.append(Iff(st, prev))
            started.append(st)

        # player p departs immediately after the last piece in which they are involved
        # finished[s]: player p is still needed in slot s or later
        finished = [None] * n
        for s in reversed(slots):
            fin = Bool(f"finished_{p}_{s}")
            nxt = plays[s] if s == n - 1 else (plays[s] | finished[s + 1])
            cons.append(Iff(fin, nxt))
            finished[s] = fin

        # total time when players are present but not currently playing
        for s in slots:
            w = Bool(f"waiting_{p}_{s}")
            cons.append(Iff(w, started[s] & finished[s] & ~plays[s]))
            waiting[p][s] = w
            slot_wait.append((p, s, w))

    # the waiting time of a player in a slot is the duration of the piece rehearsed in that slot
    total_waiting_terms = []
    for p, s, w in slot_wait:
        for j in range(n):
            a = Bool(f"wait_{p}_{s}_{j}")
            cons.append(Iff(a, w & pos[j][s]))
            total_waiting_terms.append(duration[j] * a)
    total_waiting = sum(total_waiting_terms)

    # the rehearsal order: piece rehearsed in each slot
    rehearsal_order = [sum(j * pos[j][s] for j in range(n)) for s in slots]

    return cons, {"rehearsal_order": rehearsal_order}, ("minimize", total_waiting)
