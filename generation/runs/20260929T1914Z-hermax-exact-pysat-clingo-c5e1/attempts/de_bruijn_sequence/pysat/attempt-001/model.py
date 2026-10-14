# De Bruijn sequence B(base, n): a cyclic sequence over an alphabet of `base`
# symbols, of length base**n, in which every string of n symbols occurs exactly
# once. Modelled as a cycle through all base**n windows of n consecutive symbols.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    base = instance["base"]  # size of the alphabet
    n = instance["n"]  # order: length of the strings that must all appear
    length = base**n  # length of the sequence = number of distinct strings

    pool = IDPool()
    # x[i] = the number (in the given base) read from the window starting at position i
    x = [Integer(f"x_{i}", 0, length - 1, vpool=pool) for i in range(length)]
    # binary[i][j] = j-th symbol (most significant first) of the window starting at position i
    binary = [[Integer(f"digit_{i}_{j}", 0, base - 1, vpool=pool) for j in range(n)] for i in range(length)]
    engine = IntegerEngine(vars=x + [d for row in binary for d in row], vpool=pool)

    # every possible string occurs exactly once, i.e. all window numbers differ
    engine.add_alldifferent(x)

    # link each window number to its symbols
    for i in range(length):
        engine.add_linear(sum(base ** (n - j - 1) * binary[i][j] for j in range(n)) - x[i] == 0)

    # consecutive windows overlap: window i shifted by one symbol is window i-1 ...
    for i in range(1, length):
        for j in range(1, n):
            engine.add_equal(binary[i - 1][j], binary[i][j - 1])
    # ... and the last window continues into the first one, closing the cycle
    for j in range(1, n):
        engine.add_equal(binary[length - 1][j], binary[0][j - 1])

    # the sequence is the first symbol of every window
    return engine.clausify(), {"de_bruijn": [binary[i][0] for i in range(length)]}
