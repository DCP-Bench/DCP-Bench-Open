# Autoref: find a series s[0..n+1] in which every i from 0 to n occurs exactly
# s[i] times, and whose last element s[n+1] equals m.
import cpmpy as cp


def build(instance):
    n = instance["n"]
    m = instance["m"]  # required value of the last element

    # The series has n + 2 positions; every value lies between 0 and n.
    s = cp.intvar(0, n, shape=n + 2, name="s")

    model = cp.Model()

    # The last element is m.
    model += s[n + 1] == m

    # The value i occurs exactly s[i] times in the series, for every i from 0 to n.
    for i in range(n + 1):
        model += cp.Count(s, i) == s[i]

    return model, {"s": s}
