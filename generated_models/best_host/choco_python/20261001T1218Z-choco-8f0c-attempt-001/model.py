# Best host: seat six guests around a round table so that every guest sits only next to guests
# they get along with.
from pychoco.model import Model

# The puzzle has no instance data; the guests and who gets along with whom are its statement.
ANDREW, BETTY, CARA, DAVE, ERICA, FRANK = range(6)
N_GUESTS = 6
# PREFS[g] = the only guests g will sit next to
PREFS = [
    [DAVE, FRANK],    # Andrew
    [CARA, ERICA],    # Betty
    [BETTY, FRANK],   # Cara
    [ANDREW, ERICA],  # Dave
    [BETTY, DAVE],    # Erica
    [ANDREW, CARA],   # Frank
]


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    # x[i] = the guest in seat i; seats are in order around the table
    x = [model.intvar(0, N_GUESTS - 1, name=f"x_{i}") for i in range(N_GUESTS)]

    # Every guest has one seat.
    model.all_different(x).post()

    # Neighbours at the table must both accept each other: for seats i and i+1 (wrapping round),
    # the guest in seat i+1 is in the list of the guest in seat i, and the other way round.
    good_neighbours = [(a, b) for a in range(N_GUESTS) for b in range(N_GUESTS)
                       if b in PREFS[a] and a in PREFS[b]]
    for i in range(N_GUESTS):
        model.table([x[i], x[(i + 1) % N_GUESTS]], good_neighbours).post()

    return model, {"x": x}
