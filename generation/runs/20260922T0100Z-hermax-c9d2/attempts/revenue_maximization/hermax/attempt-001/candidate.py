# Sell the mix of packages that earns most without overbooking any leg.
from dcp_maxsat import MaxSat


def build(instance):
    seats = instance["available_seats"]
    demand = instance["demand"]
    revenue = instance["revenue"]
    delta = instance["delta"]
    packages, legs = len(demand), len(seats)

    sat = MaxSat()
    sell = [sat.int(0, demand[i]) for i in range(packages)]
    for j in range(legs):
        uses = [delta[i][j] for i in range(packages)]
        sat.weighted_sum_le(uses, sell, seats[j])

    ceiling = sum(revenue[i] * demand[i] for i in range(packages))
    earned = sat.int(0, ceiling)
    sat.link_sum(list(zip(revenue, sell)), earned)
    return sat, {"packages_to_sell": sell,
                 "max_revenue": earned}, ("maximize", earned)
