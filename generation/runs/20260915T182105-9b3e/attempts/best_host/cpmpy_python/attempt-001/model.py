import cpmpy as cp


def build(instance):
    """Best host: seat six guests around a table so that each sits between the
    two people they are willing to sit next to.

    The puzzle states its own guests and preferences, so `instance` is unused.
    Guests are numbered Andrew 0, Betty 1, Cara 2, Dave 3, Erica 4, Frank 5.
    """
    del instance

    n = 6
    andrew, betty, cara, dave, erica, frank = range(n)

    prefs = cp.cpm_array([
        [dave, frank],    # Andrew
        [cara, erica],    # Betty
        [betty, frank],   # Cara
        [andrew, erica],  # Dave
        [betty, dave],    # Erica
        [andrew, cara],   # Frank
    ])

    x = cp.intvar(0, n - 1, shape=n, name="x")

    model = cp.Model(cp.AllDifferent(x))
    for i in range(n):
        # Both neighbours of the guest in seat i must be on that guest's list.
        for neighbour in (x[(i - 1) % n], x[(i + 1) % n]):
            model += cp.sum([prefs[x[i], j] == neighbour for j in range(2)]) > 0

    return model, {"x": x}
