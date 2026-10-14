"""Magic sequence: a sequence x_0..x_{n-1} where the number i occurs exactly x_i times.

Each x_i lies between 0 and n-1. For example 6, 2, 1, 0, 0, 0, 1, 0, 0, 0 is a magic
sequence of length 10: 0 occurs 6 times, 1 occurs twice, and so on.
"""
from docplex.mp.model import Model


def build(instance):
    n = instance["n"]  # length of the sequence; values run from 0 to n - 1

    model = Model("magic_sequence")

    # holds[i, v] is 1 when position i holds the value v.
    holds = model.binary_var_matrix(range(n), range(n), name="holds")

    # Every position holds exactly one value.
    for i in range(n):
        model.add_constraint(model.sum(holds[i, v] for v in range(n)) == 1)

    # x[i] is the value at position i, read back from the assignment.
    x = [model.sum(v * holds[i, v] for v in range(n)) for i in range(n)]

    # The number i occurs exactly x[i] times in the sequence: the positions that hold the
    # value i are counted through the assignment.
    for i in range(n):
        model.add_constraint(x[i] == model.sum(holds[j, i] for j in range(n)))

    return model, {"x": x}
