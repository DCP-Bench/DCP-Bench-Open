from dcp_sat import Sat


def build(instance):
    n = instance["n"]
    sat = Sat()
    x = sat.int(0, n)
    y = sat.int(0, n)
    sat.sum_eq([x, y], n)
    return sat, {"x": x, "y": y}
