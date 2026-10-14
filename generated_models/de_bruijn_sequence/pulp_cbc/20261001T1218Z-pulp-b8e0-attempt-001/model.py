"""De Bruijn sequence: a cyclic sequence over an alphabet of `base` symbols in which every
string of n symbols occurs exactly once as a window of n consecutive positions. Its length
is base ** n.

The model reports the sequence.
"""
import pulp


def build(instance):
    base = instance["base"]  # size of the alphabet, symbols are 0..base-1
    n = instance["n"]  # order: length of the windows
    m = base ** n  # length of the sequence = number of distinct windows

    problem = pulp.LpProblem("de_bruijn", pulp.LpMinimize)  # satisfaction: no objective

    # symbol[k][a] = 1 if the sequence has symbol a at position k; de_bruijn[k] reads it back
    symbol = pulp.LpVariable.dicts("symbol", (range(m), range(base)), cat="Binary")
    for k in range(m):
        problem += pulp.lpSum(symbol[k][a] for a in range(base)) == 1
    de_bruijn = [pulp.lpSum(a * symbol[k][a] for a in range(base)) for k in range(m)]

    # The window starting at position i is the number v = sum_j symbol(i + j) * base^(n-1-j),
    # positions taken cyclically. window[i][v] = 1 if the window at position i is the
    # string with number v. Each position starts exactly one window, and (all windows
    # being different, with as many windows as strings) each string is the window of
    # exactly one position.
    window = pulp.LpVariable.dicts("window", (range(m), range(m)), cat="Binary")
    for i in range(m):
        problem += pulp.lpSum(window[i][v] for v in range(m)) == 1
    for v in range(m):
        problem += pulp.lpSum(window[i][v] for i in range(m)) == 1

    def digit(v, j):
        """Symbol at place j (0 = first) of the string with number v."""
        return (v // base ** (n - 1 - j)) % base

    # The window at position i has symbol a at its place j exactly when the sequence has
    # a at position i + j: the windows whose place j is a carry the weight symbol[i + j][a].
    # (Stated as one equality per place and symbol, which is tighter than comparing every
    # window with every position.)
    for i in range(m):
        for j in range(n):
            for a in range(base):
                problem += pulp.lpSum(
                    window[i][v] for v in range(m) if digit(v, j) == a
                ) == symbol[(i + j) % m][a]

    return problem, {"de_bruijn": de_bruijn}
