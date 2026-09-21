# Make the exact amount from the available coins, using as few coins as possible.
from dcp_pb import Pb


def build(instance):
    amount = instance["amount"]
    types = instance["types_of_coins"]
    available = instance["available_coins"]
    n = len(types)

    pb = Pb()
    counts = [pb.int(0, available[i]) for i in range(n)]
    pb.weighted_sum_eq(types, counts, amount)
    pb.minimise([(1, c) for c in counts])
    return pb, {"coin_counts": counts}
