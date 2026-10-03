"""Best host: seat six guests around a round table so that every guest sits only next to the two
guests they get along with.

The model reports the guest in each seat, going around the table (Andrew 0, Betty 1, Cara 2,
Dave 3, Erica 4, Frank 5). The puzzle has no instance data; the preferences are the puzzle's own.
"""
from docplex.mp.model import Model


def build(instance):
    n = 6  # guests and seats (puzzle constant)
    Andrew, Betty, Cara, Dave, Erica, Frank = range(n)
    # The two guests each guest will sit next to (puzzle constant).
    prefs = [
        [Dave, Frank],   # Andrew
        [Cara, Erica],   # Betty
        [Betty, Frank],  # Cara
        [Andrew, Erica],  # Dave
        [Betty, Dave],   # Erica
        [Andrew, Cara],  # Frank
    ]
    seats = range(n)
    guests = range(n)

    model = Model("best_host")

    # sits[i, g] = 1 when guest g takes seat i; every seat has one guest and every guest one
    # seat (all different).
    sits = {(i, g): model.binary_var(name=f"sits_{i}_{g}") for i in seats for g in guests}
    for i in seats:
        model.add_constraint(model.sum(sits[i, g] for g in guests) == 1)
    for g in guests:
        model.add_constraint(model.sum(sits[i, g] for i in seats) == 1)

    # The guests on both sides of a seat (the table is round) are among the two the seated
    # guest will sit next to: a guest g in seat i rules out every other guest h in seats i - 1
    # and i + 1.
    for i in seats:
        for g in guests:
            for h in guests:
                if h not in prefs[g]:
                    for side in ((i - 1) % n, (i + 1) % n):
                        model.add_constraint(sits[i, g] + sits[side, h] <= 1)

    return model, {"x": [model.sum(g * sits[i, g] for g in guests) for i in seats]}
