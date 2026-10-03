# Rehearsal problem: order the pieces of a concert for rehearsal so that the
# total time players spend present but not playing is as small as possible.
# A player arrives just before the first piece they play and leaves just after
# the last one.
from hermax.model import Model


def build(instance):
    num_pieces = instance["num_pieces"]
    num_players = instance["num_players"]
    duration = instance["duration"]  # duration[j] = length of piece j
    rehearsal = instance["rehearsal"]  # rehearsal[p][j] = 1 when player p plays in piece j

    m = Model()
    # at[s][j] = piece j is rehearsed in slot s
    at = m.bool_matrix("at", num_pieces, num_pieces)
    # rehearsal_order[s] = the piece rehearsed in slot s (the declared output)
    rehearsal_order = m.int_vector("rehearsal_order", num_pieces, 0, num_pieces - 1)

    # the order is a permutation: every slot rehearses one piece and every
    # piece is rehearsed in one slot
    for s in range(num_pieces):
        m &= at.row(s).exactly_one()
    for j in range(num_pieces):
        m &= at.col(j).exactly_one()

    # rehearsal_order[s] is the piece that `at` puts in slot s
    for s in range(num_pieces):
        for j in range(num_pieces):
            m &= (~at[s][j] | (rehearsal_order[s] == j))

    for p in range(num_players):
        pieces = [j for j in range(num_pieces) if rehearsal[p][j]]  # pieces player p plays in

        # arrived[s] = player p has played in some slot up to s, so has arrived;
        # still_needed[s] = player p plays in some slot from s on, so has not left.
        # Both are only forced upward: they are true when the player plays in a
        # slot that makes them so, and the objective keeps them from being true
        # otherwise, because they can only add waiting time.
        arrived = m.bool_vector(f"arrived_{p}", num_pieces)
        still_needed = m.bool_vector(f"still_needed_{p}", num_pieces)
        # present[s] = player p is at the rehearsal during slot s
        present = m.bool_vector(f"present_{p}", num_pieces)
        for s in range(num_pieces):
            for j in pieces:
                m &= (~at[s][j] | arrived[s])
                m &= (~at[s][j] | still_needed[s])
            if s > 0:
                m &= (~arrived[s - 1] | arrived[s])
            if s + 1 < num_pieces:
                m &= (~still_needed[s + 1] | still_needed[s])
            # between the first and the last slot they play in, the player is present
            m &= (~arrived[s] | ~still_needed[s] | present[s])

        # Waiting: in a slot where player p is present but the piece rehearsed
        # does not involve them, they wait for as long as that piece lasts.
        # wait[s][j] is forced true in that case and the soft clause charges
        # duration[j] when it is true (minimising: pay when the literal is true).
        for s in range(num_pieces):
            for j in range(num_pieces):
                if not rehearsal[p][j]:
                    wait = m.bool(f"wait_{p}_{s}_{j}")
                    m &= (~at[s][j] | ~present[s] | wait)
                    m.obj[duration[j]] += ~wait

    return m, {"rehearsal_order": rehearsal_order}
