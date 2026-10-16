# Bank van coin bags: find how many bags of each type were stolen so that the stolen coins add up to the total lost.
from pyscipopt import Model, quicksum


def build(instance):
    coins = instance["coin_numbers"]
    total = instance["total_coins_lost"]
    n = len(coins)
    m = Model()
    # bags[i] = number of stolen bags of type i (each holding coins[i] coins)
    # upper bound: the stolen bags of one type cannot hold more than the total lost
    bags = [m.addVar(name=f"bags_{i}", vtype="I", lb=0, ub=total // coins[i]) for i in range(n)]
    # the stolen bags hold exactly the total number of coins lost
    m.addCons(quicksum(coins[i] * bags[i] for i in range(n)) == total)
    return m, {"bags": bags}
