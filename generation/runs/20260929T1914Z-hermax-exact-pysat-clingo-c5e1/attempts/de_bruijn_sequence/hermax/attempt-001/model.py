# De Bruijn sequence B(base, n): a cyclic sequence over an alphabet of `base`
# symbols, of length base**n, in which every string of n symbols occurs exactly
# once. Modelled as a cycle through all base**n windows of n consecutive symbols.
from hermax.model import Model


def build(instance):
    base = instance["base"]  # size of the alphabet
    n = instance["n"]  # order: length of the strings that must all appear
    length = base**n  # length of the sequence = number of distinct strings

    m = Model()
    # x[i] = the number (in the given base) read from the window starting at position i
    x = m.int_vector("x", length, 0, length - 1)
    # binary[i][j] = j-th symbol (most significant first) of the window starting at position i
    binary = m.int_matrix("binary", length, n, 0, base - 1)

    # every possible string occurs exactly once, i.e. all window numbers differ
    m &= x.all_different()

    # link each window number to its symbols
    for i in range(length):
        m &= (sum(base ** (n - j - 1) * binary[i][j] for j in range(n)) == x[i])

    # consecutive windows overlap: window i shifted by one symbol is window i-1 ...
    for i in range(1, length):
        for j in range(1, n):
            m &= (binary[i - 1][j] == binary[i][j - 1])
    # ... and the last window continues into the first one, closing the cycle
    for j in range(1, n):
        m &= (binary[length - 1][j] == binary[0][j - 1])

    # the sequence is the first symbol of every window
    return m, {"de_bruijn": [binary[i][0] for i in range(length)]}
