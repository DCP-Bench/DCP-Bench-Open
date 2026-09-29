# De Bruijn sequence B(base, n): a cyclic sequence over an alphabet of `base`
# symbols, of length base**n, in which every string of n symbols occurs exactly
# once. Modelled as a cycle through all base**n windows of n consecutive symbols.
from pychoco.model import Model


def build(instance):
    base = instance["base"]  # size of the alphabet
    n = instance["n"]  # order: length of the strings that must all appear
    m = base**n  # length of the sequence = number of distinct strings

    model = Model()

    # x[i] = the number (in the given base) read from the window starting at position i
    x = [model.intvar(0, m - 1, name=f"x_{i}") for i in range(m)]
    # binary[i][j] = j-th symbol (most significant first) of the window starting at position i
    binary = [[model.intvar(0, base - 1, name=f"digit_{i}_{j}") for j in range(n)] for i in range(m)]

    # every possible string occurs exactly once, i.e. all window numbers differ
    model.all_different(x).post()

    # link each window number to its symbols
    weights = [base ** (n - j - 1) for j in range(n)]
    for i in range(m):
        model.scalar(binary[i], weights, "=", x[i]).post()

    # consecutive windows overlap: window i shifted by one symbol is window i-1 ...
    for i in range(1, m):
        for j in range(1, n):
            model.arithm(binary[i - 1][j], "=", binary[i][j - 1]).post()
    # ... and the last window continues into the first one, closing the cycle
    for j in range(1, n):
        model.arithm(binary[m - 1][j], "=", binary[0][j - 1]).post()

    # the sequence is the first symbol of every window
    de_bruijn = [binary[i][0] for i in range(m)]

    return model, {"de_bruijn": de_bruijn}
