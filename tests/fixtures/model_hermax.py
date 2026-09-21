from dcp_maxsat import MaxSat


def build(instance):
    n = instance["n"]
    sat = MaxSat()
    x = sat.int(0, n)
    y = sat.int(0, n)
    if not instance["optimize"]:
        sat.sum_eq([x, y], n)
        return sat, {"x": x, "y": y}
    sat.sum_ge([x, y], n)
    total = sat.int(0, 2 * n)
    sat.link_sum([(1, x), (1, y)], total)
    return sat, {"x": x, "y": y}, ("minimize", total)
