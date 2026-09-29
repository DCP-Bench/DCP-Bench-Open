# De Bruijn sequence B(base, n): a cyclic sequence over an alphabet of `base`
# symbols, of length base**n, in which every string of n symbols occurs exactly
# once. Modelled as a cycle through all base**n windows of n consecutive symbols.
from exact import Exact


def build(instance):
    base = instance["base"]  # size of the alphabet
    n = instance["n"]  # order: length of the strings that must all appear
    length = base**n  # length of the sequence = number of distinct strings

    solver = Exact()
    # x[i] = the number (in the given base) read from the window starting at position i
    x = [f"x_{i}" for i in range(length)]
    # binary[i][j] = j-th symbol (most significant first) of the window starting at position i
    binary = [[f"digit_{i}_{j}" for j in range(n)] for i in range(length)]
    # is_[i][v] is 1 exactly when window i reads the number v; all numbers differ
    is_ = [{} for _ in range(length)]
    for i in range(length):
        solver.addVariable(x[i], 0, length - 1)
        for name in binary[i]:
            solver.addVariable(name, 0, base - 1)
        for v in range(length):
            is_[i][v] = f"is_{i}_{v}"
            solver.addVariable(is_[i][v], 0, 1)
        solver.addConstraint([(1, is_[i][v]) for v in range(length)], True, 1, True, 1)
        solver.addConstraint([(v, is_[i][v]) for v in range(1, length)] + [(-1, x[i])], True, 0, True, 0)
    # every possible string occurs exactly once, i.e. all window numbers differ
    for v in range(length):
        solver.addConstraint([(1, is_[i][v]) for i in range(length)], True, 1, True, 1)

    # link each window number to its symbols
    for i in range(length):
        solver.addConstraint([(base ** (n - j - 1), binary[i][j]) for j in range(n)] + [(-1, x[i])],
                             True, 0, True, 0)

    # consecutive windows overlap: window i shifted by one symbol is window i-1 ...
    for i in range(1, length):
        for j in range(1, n):
            solver.addConstraint([(1, binary[i - 1][j]), (-1, binary[i][j - 1])], True, 0, True, 0)
    # ... and the last window continues into the first one, closing the cycle
    for j in range(1, n):
        solver.addConstraint([(1, binary[length - 1][j]), (-1, binary[0][j - 1])], True, 0, True, 0)

    # the sequence is the first symbol of every window
    return solver, {"de_bruijn": [binary[i][0] for i in range(length)]}
