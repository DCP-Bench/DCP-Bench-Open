# Subset sum (stolen coin bags): find how many bags of each size were stolen so that the stolen
# bags hold exactly the number of coins that were lost.
from exact import Exact


def build(instance):
    total_coins_lost = instance["total_coins_lost"]  # coins lost in total
    coin_numbers = instance["coin_numbers"]  # coins in one bag of each type
    n = len(coin_numbers)

    solver = Exact()

    # bags[i] = number of stolen bags of type i; as in the reference it is between 0 and the
    # total number of coins lost
    bags = [f"bags_{i}" for i in range(n)]
    for name in bags:
        solver.addVariable(name, 0, total_coins_lost)

    # the total number of coins lost equals the coins in the stolen bags
    solver.addConstraint([(coin_numbers[i], bags[i]) for i in range(n) if coin_numbers[i]],
                         True, total_coins_lost, True, total_coins_lost)

    return solver, {"bags": bags}
