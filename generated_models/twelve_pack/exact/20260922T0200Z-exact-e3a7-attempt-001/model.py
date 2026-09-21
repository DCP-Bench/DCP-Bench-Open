# Fewest items from whole packs that still meet the target.
from dcp_pb import Pb


def build(instance):
    packs = instance["packs"]
    target = instance["target"]
    n = len(packs)

    # The reference allows up to twice the target of each pack size.
    ceiling = target * 2
    pb = Pb()
    counts = pb.ints(n, 0, ceiling)
    total = pb.int(0, ceiling * n)
    pb.eq(list(zip(packs, counts)) + [(-1, total)], 0)
    pb.ge([(1, total)], target)
    pb.minimise([(1, total)])
    return pb, {"counts": counts}
