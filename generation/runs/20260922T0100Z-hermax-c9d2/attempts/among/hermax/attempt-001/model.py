# Exactly m of the n variables take a value from v.
from dcp_maxsat import MaxSat


def build(instance):
    n = instance["n"]
    wanted = instance["m"]
    values = instance["v"]

    sat = MaxSat()
    # 0..7 is the domain the problem statement fixes, not an instance field.
    x = sat.ints(n, 0, 7)
    hits = [x[i].literal(value) for i in range(n) for value in values
            if x[i].literal(value) is not None]
    sat.exactly(hits, wanted)
    return sat, {"x": x}
