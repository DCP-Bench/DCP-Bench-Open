# de Bruijn sequence B(base, n): a cyclic sequence of length base**n over an alphabet of
# `base` symbols in which every string of length n occurs exactly once as a substring.
import cpmpy as cp


def build(instance):
    base = instance["base"]      # size of the alphabet
    n = instance["n"]            # length of the substrings
    m = base ** n                # length of the sequence = number of distinct strings

    # x[i] is the number (in 0..m-1) read from the string of n symbols starting at position i.
    x = cp.intvar(0, m - 1, shape=m, name="x")
    # binary[i] holds those n symbols (most significant first).
    binary = cp.intvar(0, base - 1, shape=(m, n), name="binary")
    # de_bruijn[i] is the symbol at position i of the sequence.
    de_bruijn = cp.intvar(0, base - 1, shape=m, name="de_bruijn")

    model = cp.Model()

    # Every string of length n occurs exactly once, i.e. all the numbers differ.
    model += cp.AllDifferent(x)

    # x[i] is the number whose digits (in the given base) are binary[i].
    for i in range(m):
        model += x[i] == cp.sum([binary[i, j] * base ** (n - j - 1) for j in range(n)])

    # Consecutive strings overlap: dropping the first symbol of the string at i-1 gives the
    # first n-1 symbols of the string at i.
    for i in range(1, m):
        for j in range(1, n):
            model += binary[i - 1, j] == binary[i, j - 1]

    # The sequence is cyclic, so the last string also overlaps with the first one.
    for j in range(1, n):
        model += binary[m - 1, j] == binary[0, j - 1]

    # The sequence itself is the first symbol of each string.
    for i in range(m):
        model += de_bruijn[i] == binary[i, 0]

    return model, {"de_bruijn": de_bruijn}
