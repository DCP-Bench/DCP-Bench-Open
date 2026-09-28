"""Money change: pay the amount exactly from the coins available, using as few coins as possible."""
from docplex.mp.model import Model


def build(instance):
    values = instance["types_of_coins"]      # value of each type of coin
    available = instance["available_coins"]  # how many coins of each type Alice has

    model = Model("money_change")

    # coin_counts[i] is how many coins of type i Alice gives, at most the number
    # she has of that type.
    coin_counts = [model.integer_var(0, available[i], name=f"coin_counts_{i}") for i in range(len(values))]

    # The coins given add up to the amount owed.
    model.add_constraint(model.dot(coin_counts, values) == instance["amount"], ctname="amount")

    # Minimise the number of coins given.
    model.minimize(model.sum(coin_counts))

    return model, {"coin_counts": coin_counts}
