"""Circular table (Hearts): three players X, Y, Z of different nationalities (American, English, French) sit
around a table in seats 0, 1, 2. Each player passed cards to the person on their right. Seat 1 is right of
seat 0, seat 2 is right of seat 1, and seat 0 follows seat 2 around the table. Output: the seat of each player
and of each nationality, so that equal values mean the same person."""
from paramita.modelling import Bool, Iff

SEATS = range(3)


def seat_vars(name):
    # one-hot seat: sv[v] is true when the person or nationality `name` sits in seat v
    return {v: Bool(f"{name}_seat_{v}") for v in SEATS}


def seat_value(sv):
    # the seat number as an integer expression
    return sum(v * sv[v] for v in SEATS)


def build(instance):
    cons = []

    x, y, z = seat_vars("X"), seat_vars("Y"), seat_vars("Z")
    am, en, fr = seat_vars("american"), seat_vars("english"), seat_vars("french")

    # each player sits in exactly one seat and no two players share a seat
    for sv in (x, y, z):
        cons.append(sum(sv.values()) == 1)
    for v in SEATS:
        cons.append(x[v] + y[v] + z[v] == 1)

    # each nationality belongs to exactly one seat and the three nationalities are all different
    for sv in (am, en, fr):
        cons.append(sum(sv.values()) == 1)
    for v in SEATS:
        cons.append(am[v] + en[v] + fr[v] == 1)

    # Y passed three hearts to the American, so the American sits on Y's right: american = y + 1 (mod 3)
    for v in SEATS:
        cons.append(Iff(y[v], am[(v + 1) % 3]))

    # X passed the queen of spades and two diamonds to the person who passed their cards to the Frenchwoman.
    # X passed to the person on X's right, at x + 1; that person passed to the Frenchwoman on their right,
    # so the Frenchwoman sits at x + 2 (mod 3)
    for v in SEATS:
        cons.append(Iff(x[v], fr[(v + 2) % 3]))

    outputs = {
        "x": seat_value(x),
        "y": seat_value(y),
        "z": seat_value(z),
        "american": seat_value(am),
        "english": seat_value(en),
        "french": seat_value(fr),
    }
    return cons, outputs
