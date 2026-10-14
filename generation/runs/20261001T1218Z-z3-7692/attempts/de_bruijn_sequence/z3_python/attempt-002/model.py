# De Bruijn sequence: a cyclic sequence over an alphabet of `base` symbols in
# which every string of length n occurs exactly once as a window.
import itertools

import z3


def build(instance):
    base = instance["base"]  # size of the alphabet (symbols 0..base-1)
    n = instance["n"]        # order: length of the strings
    m = base ** n            # length of the sequence = number of distinct strings

    # de_bruijn[i] is the symbol at position i of the (cyclic) sequence.
    de_bruijn = [z3.Int(f"de_bruijn_{i}") for i in range(m)]

    solver = z3.Solver()

    for symbol in de_bruijn:
        solver.add(symbol >= 0, symbol <= base - 1)

    # The window starting at position i is the n symbols de_bruijn[i], de_bruijn[i + 1],
    # ... read cyclically (position m wraps round to 0). Every string of n symbols
    # must occur as the window at exactly one position. The reference reaches this
    # by giving each window a number 0..m-1 and making the numbers all different;
    # saying it per string, with Boolean "window i spells string w" tests, is a
    # pigeonhole-friendly form that Z3 solves much faster than a Distinct over sums.
    is_symbol = [[de_bruijn[i] == s for s in range(base)] for i in range(m)]
    for string in itertools.product(range(base), repeat=n):
        spells = [z3.And([is_symbol[(i + j) % m][string[j]] for j in range(n)])
                  for i in range(m)]
        solver.add(z3.PbEq([(w, 1) for w in spells], 1))

    return solver, {"de_bruijn": de_bruijn}
