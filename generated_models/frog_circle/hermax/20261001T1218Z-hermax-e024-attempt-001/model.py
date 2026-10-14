# Frog circle: arrange the cards 1..n in a circle so that a frog that starts on
# card 1 and, from card k, jumps k places clockwise lands on every card.
from hermax.model import Model


def build(instance):
    n = instance["n"]

    m = Model()
    # x[q] = the card at position q of the circle (the declared output)
    x = m.int_vector("x", n, 1, n)
    # card[q][v - 1] = position q holds card v (one-hot form of x)
    card = m.bool_matrix("card", n, n)

    # the arrangement uses every card once: one card per position, one position per card
    for q in range(n):
        m &= card.row(q).exactly_one()
        m &= card.col(q).exactly_one()
    for q in range(n):
        for v in range(1, n + 1):
            m &= (~card[q][v - 1] | (x[q] == v))

    # The frog starts on card 1, which sits at position 0.
    m &= card[0][0]

    # at[i][q] = after i jumps the frog is at position q
    at = m.bool_matrix("at", n, n)
    m &= at[0][0]
    # Each jump takes the frog from position q holding card v to position (q + v) mod n.
    for i in range(n - 1):
        for q in range(n):
            for v in range(1, n + 1):
                m &= (~at[i][q] | ~card[q][v - 1] | at[i + 1][(q + v) % n])
    # The frog is at exactly one position after each of its n - 1 jumps (the
    # starting position included) and the positions are all different, so it
    # lands on every card.
    for i in range(n):
        m &= at.row(i).exactly_one()
    for q in range(n):
        m &= at.col(q).exactly_one()

    return m, {"x": x}
