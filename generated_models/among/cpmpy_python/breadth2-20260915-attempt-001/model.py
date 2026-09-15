import cpmpy as cp

# The reference's own domain for x.
LOW, HIGH = 0, 7


def build(instance):
    n, wanted, values = instance["n"], instance["m"], instance["v"]
    x = cp.intvar(LOW, HIGH, shape=n, name="x")
    model = cp.Model(cp.sum([x[i] == value for i in range(n) for value in values]) == wanted)
    return model, {"x": [x[i] for i in range(n)]}
