# Autoref: find a series s[0..n+1] in which every i from 0 to n occurs exactly
# s[i] times, and whose last element s[n+1] equals m.
from pychoco.model import Model


def build(instance):
    n = instance["n"]
    m = instance["m"]  # required value of the last element

    model = Model()

    # the series has n + 2 positions; every value lies between 0 and n
    s = [model.intvar(0, n, name=f"s_{k}") for k in range(n + 2)]

    # the last element is m
    model.arithm(s[n + 1], "=", m).post()

    # the value i occurs exactly s[i] times in the series
    for i in range(n + 1):
        model.count(i, s, s[i]).post()

    return model, {"s": s}
