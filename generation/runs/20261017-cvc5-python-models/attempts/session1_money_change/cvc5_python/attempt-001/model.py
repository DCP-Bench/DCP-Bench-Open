# Money change: Alice has to give Bob some change with coins of different values.
# She has a certain number of coins of each value available. The change is composed
# from the available coins minimizing the number of coins used. Output coin_counts:
# the number of coins of each type to give to Bob.
import cvc5.pythonic as cz


def build(instance):
    amount = instance["amount"]
    values = instance["types_of_coins"]
    available = instance["available_coins"]
    n = len(values)

    # Decision: number of coins of each type given to Bob.
    coin_counts = cz.Ints(" ".join(f"coin_counts_{i}" for i in range(n))) if n > 1 else [cz.Int("coin_counts_0")]

    # Each count is between 0 and the number of coins available of that type.
    # Coins available of each type bound the count.
    bounds = []
    for i in range(n):
        bounds.append(coin_counts[i] >= 0)
        bounds.append(coin_counts[i] <= available[i])

    # The change must add up to the amount, using the values of the coins.
    # The coins given must have a total value equal to the amount.
    total_value = cz.Sum([coin_counts[i] * values[i] for i in range(n)])
    amount_constraint = [total_value == amount]

    # The number of coins used is the objective to minimize.
    number_of_coins = cz.Sum(coin_counts)

    constraints = bounds + amount_constraint
    return constraints, {"coin_counts": coin_counts}, ("minimize", number_of_coins)
