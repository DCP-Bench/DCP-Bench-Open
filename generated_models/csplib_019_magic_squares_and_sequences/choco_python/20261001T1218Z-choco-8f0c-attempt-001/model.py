# Magic sequence: a sequence x_0..x_{n-1} of integers in 0..n-1 in which the
# number i occurs exactly x_i times, for every i.
from pychoco.model import Model


def build(instance):
    n = instance["n"]  # length of the sequence

    model = Model()

    x = [model.intvar(0, n - 1, name=f"x_{i}") for i in range(n)]

    # for every i, the number i occurs exactly x[i] times in the sequence
    for i in range(n):
        model.count(i, x, x[i]).post()

    return model, {"x": x}
