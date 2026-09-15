import math

from ortools.sat.python import cp_model


def build(instance):
    """Handshaking: at a dinner of couples, nobody shakes their own or their
    spouse's hand, and everybody but Hilary reports a different count.
    """
    num_couples = instance["num_couples"]
    # Hilary and Jocelyn plus the invited couples, laid out as
    # Pair1a, Pair1b, Pair2a, Pair2b, ... with Hilary at 0 and Jocelyn at 1.
    n = 2 + num_couples * 2

    model = cp_model.CpModel()
    x = [model.new_int_var(0, n - 2, f"x{i}") for i in range(n)]
    hil = x[0]
    y = [[model.new_bool_var(f"y{i}_{j}") for j in range(n)] for i in range(n)]

    # Every count except Hilary's is different.
    model.add_all_different(x[1:])

    for i in range(math.ceil(n / 2)):
        # Nobody shakes hands with their spouse.
        model.add(y[2 * i][2 * i + 1] == 0)
        model.add(y[2 * i + 1][2 * i] == 0)

    for i in range(n):
        # Nobody shakes their own hand, and x counts the hands they shook.
        model.add(y[i][i] == 0)
        model.add(x[i] == sum(y[i]))

    for i in range(n):
        for j in range(n):
            # Handshaking is mutual.
            model.add(y[i][j] == y[j][i])

    return model, {"hil": hil}
