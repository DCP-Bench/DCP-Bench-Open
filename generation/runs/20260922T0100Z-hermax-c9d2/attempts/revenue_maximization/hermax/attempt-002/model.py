# Sell the mix of packages that earns most without overbooking any leg.
#
# The objective variable is one-hot encoded, so its domain is its cost. A plain
# 0..sum(revenue*demand) range here is 9001 values, which exhausts the memory
# limit while the objective is being tied to the expression. Only totals the
# revenues can actually add up to are reachable, and there are far fewer of
# them, so the domain is built from those.
from dcp_maxsat import MaxSat


def reachable(revenue, demand):
    totals = {0}
    for price, most in zip(revenue, demand):
        totals = {total + price * count for total in totals for count in range(most + 1)}
    return sorted(totals)


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

    earned = sat.int_from(reachable(revenue, demand))
    sat.link_sum(list(zip(revenue, sell)), earned)
    return sat, {"packages_to_sell": sell,
                 "max_revenue": earned}, ("maximize", earned)
