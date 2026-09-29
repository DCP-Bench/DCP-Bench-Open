# Autoref: find a series s[0..n+1] in which every i from 0 to n occurs exactly
# s[i] times, and whose last element s[n+1] equals m.
from hermax.model import Model


def build(instance):
    n = instance["n"]
    last_value = instance["m"]  # required value of the last element

    model = Model()
    # the series has n + 2 positions; every value lies between 0 and n
    s = model.int_vector("s", n + 2, 0, n)

    # the last element is m
    model &= (s[n + 1] == last_value)

    # the value i occurs exactly s[i] times in the series
    for i in range(n + 1):
        model &= (sum(1 * (s[k] == i) for k in range(n + 2)) == s[i])

    return model, {"s": s}
