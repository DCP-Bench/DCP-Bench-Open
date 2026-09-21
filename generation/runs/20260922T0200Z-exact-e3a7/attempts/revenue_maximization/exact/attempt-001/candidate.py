# Sell the mix of packages that earns most without overbooking any leg.
#
# Exact takes integer variables natively, so the revenue total needs no encoding
# and the wide range that defeated the one-hot integrations costs nothing here.
from dcp_pb import Pb


def build(instance):
    seats = instance["available_seats"]
    demand = instance["demand"]
    revenue = instance["revenue"]
    delta = instance["delta"]
    packages, legs = len(demand), len(seats)

    pb = Pb()
    sell = [pb.int(0, demand[i]) for i in range(packages)]
    for j in range(legs):
        pb.le([(delta[i][j], sell[i]) for i in range(packages)], seats[j])

    ceiling = sum(revenue[i] * demand[i] for i in range(packages))
    earned = pb.int(0, ceiling)
    pb.eq(list(zip(revenue, sell)) + [(-1, earned)], 0)
    pb.maximise([(1, earned)])
    return pb, {"packages_to_sell": sell, "max_revenue": earned}
