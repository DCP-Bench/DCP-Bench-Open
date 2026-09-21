from dcp_pb import Pb


def build(instance):
    n = instance["n"]
    pb = Pb()
    x = pb.int(0, n)
    y = pb.int(0, n)
    if not instance["optimize"]:
        pb.sum_eq([x, y], n)
        return pb, {"x": x, "y": y}
    pb.sum_ge([x, y], n)
    pb.minimise([(1, x), (1, y)])
    return pb, {"x": x, "y": y}
