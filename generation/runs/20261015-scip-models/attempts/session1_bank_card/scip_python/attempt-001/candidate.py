# Bank card PIN abcd: find the 4-digit PIN (a, b, c, d) that satisfies the three facts.
from pyscipopt import Model, quicksum

DIGITS = range(10)
NAMES = ["a", "b", "c", "d"]


def build(instance):
    m = Model()
    m.hideOutput()

    # each digit takes one value 0-9: one-hot binaries b[k, v], digit value is their weighted sum
    val = {}
    b = {}
    for k in NAMES:
        val[k] = m.addVar(name=k, vtype="I", lb=0, ub=9)
        for v in DIGITS:
            b[k, v] = m.addVar(name=f"b_{k}_{v}", vtype="B")
        # each digit has exactly one value
        m.addCons(quicksum(b[k, v] for v in DIGITS) == 1)
        m.addCons(val[k] == quicksum(v * b[k, v] for v in DIGITS))

    # no two digits are the same: each value is used by at most one digit
    for v in DIGITS:
        m.addCons(quicksum(b[k, v] for k in NAMES) <= 1)

    # the 2-digit number cd is 3 times the 2-digit number ab
    m.addCons(10 * val["c"] + val["d"] == 3 * (10 * val["a"] + val["b"]))

    # the 2-digit number da is 2 times the 2-digit number bc
    m.addCons(10 * val["d"] + val["a"] == 2 * (10 * val["b"] + val["c"]))

    # the output gives the PIN digits
    outputs = {k: val[k] for k in NAMES}
    return m, outputs
