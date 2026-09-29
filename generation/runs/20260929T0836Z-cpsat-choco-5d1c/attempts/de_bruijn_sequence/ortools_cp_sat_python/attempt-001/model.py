# De Bruijn sequence B(base, n): a cyclic sequence over an alphabet of `base`
# symbols, of length base**n, in which every string of n symbols occurs exactly
# once. Modelled as a cycle through all base**n windows of n consecutive symbols.
from ortools.sat.python import cp_model


def build(instance):
    base = instance["base"]  # size of the alphabet
    n = instance["n"]  # order: length of the strings that must all appear
    m = base**n  # length of the sequence = number of distinct strings

    model = cp_model.CpModel()

    # x[i] = the number (in the given base) read from the window starting at position i
    x = [model.new_int_var(0, m - 1, f"x_{i}") for i in range(m)]
    # binary[i][j] = j-th symbol (most significant first) of the window starting at position i
    binary = [[model.new_int_var(0, base - 1, f"digit_{i}_{j}") for j in range(n)] for i in range(m)]
    # the sequence itself: the first symbol of each window
    de_bruijn = [model.new_int_var(0, base - 1, f"de_bruijn_{i}") for i in range(m)]

    # every possible string occurs exactly once, i.e. all window numbers differ
    model.add_all_different(x)

    # link each window number to its symbols
    for i in range(m):
        model.add(x[i] == sum(binary[i][j] * base ** (n - j - 1) for j in range(n)))

    # consecutive windows overlap: window i shifted by one symbol is window i-1 ...
    for i in range(1, m):
        for j in range(1, n):
            model.add(binary[i - 1][j] == binary[i][j - 1])
    # ... and the last window continues into the first one, closing the cycle
    for j in range(1, n):
        model.add(binary[m - 1][j] == binary[0][j - 1])

    # the sequence is the first symbol of every window
    for i in range(m):
        model.add(de_bruijn[i] == binary[i][0])

    return model, {"de_bruijn": de_bruijn}
