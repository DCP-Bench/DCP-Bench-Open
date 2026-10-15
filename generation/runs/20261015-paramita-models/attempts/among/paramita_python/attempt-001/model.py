# Requires exactly m values in x to take one of the values in v.
# Every entry of x is one of the values 0..7 (one-hot Bools X[i][d] per entry i and value d).
# Output x[i] is the value of the entry, sum of d * X[i][d].
from paramita.modelling import Bool

DOMAIN = range(8)


def build(instance):
    n, m, v = instance["n"], instance["m"], instance["v"]
    X = [{d: Bool(f"x_{i}_{d}") for d in DOMAIN} for i in range(n)]
    cons = []

    # every entry of x takes exactly one value between 0 and 7
    for i in range(n):
        cons.append(sum(X[i].values()) == 1)

    # exactly m values in x take one of the values in v
    # (inV[i] is 1 when entry i takes a value from v)
    inV = [sum(X[i][d] for d in v) for i in range(n)]
    cons.append(sum(inV) == m)

    x = [sum(d * X[i][d] for d in DOMAIN) for i in range(n)]
    return cons, {"x": x}
