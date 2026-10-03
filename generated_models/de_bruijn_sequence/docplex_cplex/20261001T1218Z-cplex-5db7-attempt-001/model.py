"""De Bruijn sequence: a cyclic sequence of base**n digits in 0..base-1 in which every word of n
digits appears exactly once as a window of n consecutive digits (reading around the end).

The model reports the sequence.
"""
from docplex.mp.model import Model


def build(instance):
    base = instance["base"]  # size of the alphabet
    n = instance["n"]        # order: the length of the words
    m = base ** n            # number of words, and length of the sequence

    model = Model("de_bruijn_sequence")
    positions = range(m)

    # de_bruijn[i] is the digit at position i, in 0..base-1 (a binary for base 2).
    if base == 2:
        de_bruijn = [model.binary_var(name=f"digit_{i}") for i in positions]
    else:
        de_bruijn = [model.integer_var(0, base - 1, name=f"digit_{i}") for i in positions]

    # x[i] is the number whose base-`base` digits are the window starting at position i, the
    # first digit most significant; the windows wrap around the end of the sequence. This is
    # the reference's de Bruijn property (window i + 1 is window i shifted by one digit) with
    # the shared digits stored once.
    x = [model.sum(de_bruijn[(i + j) % m] * base ** (n - j - 1) for j in range(n)) for i in positions]

    # All windows are different numbers. Each pair of windows gets one binary saying which of the
    # two is smaller. An assignment matrix of windows to words would need m * m = 1024 binaries
    # for base 2 and order 5, over the Community Edition's 1000 variables; the pairs need
    # m * (m - 1) / 2, each with two indicator constraints: 992 constraints for base 2 and
    # order 5, which is why the digits are single variables rather than one-hot binaries.
    for i in positions:
        for k in range(i + 1, m):
            smaller = model.binary_var(name=f"smaller_{i}_{k}")
            model.add_indicator(smaller, x[i] + 1 <= x[k], active_value=1)
            model.add_indicator(smaller, x[k] + 1 <= x[i], active_value=0)

    return model, {"de_bruijn": de_bruijn}
