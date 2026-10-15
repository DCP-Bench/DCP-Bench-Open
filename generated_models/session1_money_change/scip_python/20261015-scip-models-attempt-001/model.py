# Money change: pay an amount with the fewest coins, using at most the number of coins available of each type.
from pyscipopt import Model, quicksum


def build(instance):
    amount = instance["amount"]
    values = instance["types_of_coins"]
    available = instance["available_coins"]
    # one count per coin type; the number of types comes from the instance data
    K = len(values)

    m = Model()
    # coin_counts[k] = number of coins of type k given to Bob
    # upper bound: the stock of that type, and no more coins than fit in the amount
    coins = [m.addVar(name=f"coins_{k}", vtype="I", lb=0,
                      ub=min(available[k], amount // values[k]))
             for k in range(K)]

    # the coins given must add up to exactly the amount
    m.addCons(quicksum(values[k] * coins[k] for k in range(K)) == amount)

    # minimise the total number of coins used
    m.setObjective(quicksum(coins[k] for k in range(K)), "minimize")

    return m, {"coin_counts": coins}
