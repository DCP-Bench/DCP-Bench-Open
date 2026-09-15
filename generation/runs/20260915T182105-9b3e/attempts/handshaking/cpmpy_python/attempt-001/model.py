import cpmpy as cp
import math


def build(instance):
    """Handshaking: at a dinner of couples, nobody shakes their own or their
    spouse's hand, and everybody but Hilary reports a different count.
    """
    num_couples = instance["num_couples"]
    # Hilary and Jocelyn plus the invited couples, laid out as
    # Pair1a, Pair1b, Pair2a, Pair2b, ... with Hilary at 0 and Jocelyn at 1.
    n = 2 + num_couples * 2

    x = cp.intvar(0, n - 2, shape=n, name="x")
    hil = x[0]
    y = cp.boolvar(shape=(n, n), name="y")

    model = cp.Model()
    # Every count except Hilary's is different.
    model += cp.AllDifferent(x[1:])

    for i in range(math.ceil(n / 2)):
        # Nobody shakes hands with their spouse.
        model += y[2 * i, 2 * i + 1] == 0
        model += y[2 * i + 1, 2 * i] == 0

    for i in range(n):
        # Nobody shakes their own hand, and x counts the hands they shook.
        model += y[i, i] == 0
        model += x[i] == cp.sum(y[i])

    for i in range(n):
        for j in range(n):
            # Handshaking is mutual.
            model += y[i, j] == y[j, i]

    return model, {"hil": hil}
