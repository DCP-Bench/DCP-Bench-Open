# How many bags of each coin type were stolen, given the total coins lost.
from dcp_sat import Sat


def build(instance):
    coin_numbers = instance["coin_numbers"]
    total = instance["total_coins_lost"]

    sat = Sat()
    # No bag type can appear more often than the total allows, which keeps the
    # one-hot encoding to the values that can actually occur.
    bags = [sat.int(0, total // value if value else total) for value in coin_numbers]
    sat.weighted_sum_eq(coin_numbers, bags, total)
    return sat, {"bags": bags}
