# Rehearsal problem: order the pieces of a concert for rehearsal so that the
# total time players spend present but not playing is minimal. A player arrives
# just before the first piece they play in and leaves after the last one.
import z3


def build(instance):
    n_pieces = instance["num_pieces"]
    n_players = instance["num_players"]
    duration = instance["duration"]  # rehearsal time of each piece
    rehearsal = instance["rehearsal"]  # rehearsal[p][j] = 1 if player p plays in piece j

    solver = z3.Solver()

    # rehearsal_order[i] = the piece rehearsed in slot i; each piece is rehearsed exactly once
    rehearsal_order = [z3.Int(f"order_{i}") for i in range(n_pieces)]
    for piece in rehearsal_order:
        solver.add(piece >= 0, piece < n_pieces)
    solver.add(z3.Distinct(rehearsal_order))

    def by_piece(piece, table):
        """table[piece] for a piece that is a variable: Z3 has no element
        constraint, so it is an If chain over the pieces."""
        value = table[n_pieces - 1]
        for k in range(n_pieces - 2, -1, -1):
            value = z3.If(piece == k, table[k], value)
        return value

    # arrival[p] / departure[p] = first / last slot in which player p is present
    arrival = [z3.Int(f"arrival_{p}") for p in range(n_players)]
    departure = [z3.Int(f"departure_{p}") for p in range(n_players)]
    for p in range(n_players):
        solver.add(arrival[p] >= 0, arrival[p] <= n_pieces - 1, departure[p] >= 0, departure[p] <= n_pieces - 1)

    waiting = []
    for p in range(n_players):
        for i in range(n_pieces):
            plays = by_piece(rehearsal_order[i], rehearsal[p]) == 1
            present = z3.And(arrival[p] <= i, i <= departure[p])
            # a player who plays in slot i must be present in it
            solver.add(z3.Implies(plays, present))
            # waiting = present but not playing; it costs the length of the piece in that slot
            waiting.append(z3.If(z3.And(present, z3.Not(plays)), by_piece(rehearsal_order[i], duration), 0))

    # minimise the total time players spend waiting
    return solver, {"rehearsal_order": rehearsal_order}, ("minimize", z3.Sum(waiting))
