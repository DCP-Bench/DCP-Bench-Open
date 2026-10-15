from pyscipopt import Model, quicksum

# de Bruijn sequence: a cyclic sequence over an alphabet of size base in which
# every string of length n occurs exactly once as a (cyclic) substring.
def build(instance):
    base = instance["base"]
    n = instance["n"]
    # the sequence has base^n symbols, one per length-n window
    L = base ** n

    m = Model()

    # digit[i]: the i-th symbol of the sequence, from 0 to base-1
    digit = [m.addVar(name=f"digit_{i}", vtype="I", lb=0, ub=base - 1) for i in range(L)]

    # window[i] is the number of the length-n string starting at position i,
    # read as a base-`base` number (the window is cyclic, so positions wrap)
    # one-hot: at[i, s] = 1 if the window starting at i is the string s
    at = {(i, s): m.addVar(name=f"at_{i}_{s}", vtype="B") for i in range(L) for s in range(L)}
    for i in range(L):
        # each window starts with exactly one string
        m.addCons(quicksum(at[i, s] for s in range(L)) == 1)
        # the window's value equals the number of its one-hot string
        window_value = quicksum(
            base ** (n - 1 - j) * digit[(i + j) % L] for j in range(n)
        )
        m.addCons(window_value == quicksum(s * at[i, s] for s in range(L)))

    # every length-n string occurs exactly once among the L cyclic windows
    # (there are L windows and L strings, so each string is used once)
    for s in range(L):
        m.addCons(quicksum(at[i, s] for i in range(L)) == 1)

    # satisfaction problem: no objective

    outputs = {"de_bruijn": digit}
    return m, outputs
