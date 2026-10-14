"""Subset sum: find how many bags of each size the thieves took, given the total number of coins lost."""
from docplex.mp.model import Model


def build(instance):
    total = instance["total_coins_lost"]
    coins = instance["coin_numbers"]  # coins[i]: coins in a bag of type i

    model = Model("subset_sum")

    # bags[i] is the number of bags of type i stolen; the reference bounds it by
    # the total number of coins lost.
    bags = model.integer_var_list(len(coins), 0, total, name="bags")

    # The coins in the stolen bags add up to the coins lost.
    model.add_constraint(model.dot(bags, coins) == total, ctname="total")

    return model, {"bags": bags}
