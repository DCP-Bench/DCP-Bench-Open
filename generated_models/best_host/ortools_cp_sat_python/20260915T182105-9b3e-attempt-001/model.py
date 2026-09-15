from ortools.sat.python import cp_model


def build(instance):
    """Best host: seat six guests around a table so that each sits between the
    two people they are willing to sit next to.

    The puzzle states its own guests and preferences, so `instance` is unused.
    Guests are numbered Andrew 0, Betty 1, Cara 2, Dave 3, Erica 4, Frank 5.
    """
    del instance

    n = 6
    andrew, betty, cara, dave, erica, frank = range(n)

    prefs = [
        [dave, frank],    # Andrew
        [cara, erica],    # Betty
        [betty, frank],   # Cara
        [andrew, erica],  # Dave
        [betty, dave],    # Erica
        [andrew, cara],   # Frank
    ]

    model = cp_model.CpModel()
    x = [model.new_int_var(0, n - 1, f"x{i}") for i in range(n)]
    model.add_all_different(x)

    # The preference table is read at a row chosen by a decision variable, so
    # each column becomes a constant array indexed with AddElement.
    columns = [[prefs[guest][j] for guest in range(n)] for j in range(2)]

    for i in range(n):
        allowed = []
        for j in range(2):
            picked = model.new_int_var(0, n - 1, f"pref{i}_{j}")
            model.add_element(x[i], columns[j], picked)
            allowed.append(picked)
        # Both neighbours must appear among the two allowed names.
        for side, neighbour in (("prev", x[(i - 1) % n]), ("next", x[(i + 1) % n])):
            matches = []
            for j in range(2):
                same = model.new_bool_var(f"m{i}_{j}_{side}")
                model.add(allowed[j] == neighbour).only_enforce_if(same)
                model.add(allowed[j] != neighbour).only_enforce_if(~same)
                matches.append(same)
            model.add_bool_or(matches)

    return model, {"x": x}
