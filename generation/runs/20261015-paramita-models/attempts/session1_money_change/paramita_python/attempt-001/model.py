# Change-making with limited coins: pay the amount to Bob with the fewest coins,
# using at most the available number of coins of each type.
from paramita.modelling import Bool, If


def build(instance):
    amount = instance["amount"]
    values = instance["types_of_coins"]
    available = instance["available_coins"]
    k_types = len(values)

    # unary encoding of the number of coins of each type:
    # u[k][j] = 1 when at least j+1 coins of type k are given to Bob
    # the list has one bit per available coin, so the count cannot exceed the availability
    u = [[Bool(f"coin_{k}_ge_{j + 1}") for j in range(available[k])] for k in range(k_types)]

    def count(k):
        return sum(u[k])

    cons = []

    # the number of coins of each type given is at most the number available
    # (enforced by the length of the unary list) and the bits are ordered, so the
    # count is the number of true bits
    for k in range(k_types):
        for j in range(available[k] - 1):
            cons.append(If(u[k][j + 1], u[k][j]))

    # the change has to add up to the amount: the coins given sum to the amount
    cons.append(sum(values[k] * b for k in range(k_types) for b in u[k]) == amount)

    # minimise the number of coins used
    total_coins = sum(b for k in range(k_types) for b in u[k])

    # coin_counts[k] is the number of coins of type k given to Bob
    coin_counts = [count(k) for k in range(k_types)]
    return cons, {"coin_counts": coin_counts}, ("minimize", total_coins)
