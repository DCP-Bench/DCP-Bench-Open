# Subset sum with bags of coins: a bank van had several bags of coins, each
# containing a number of coins from a given list (there are multiple bags of the
# same kind). Some bags were stolen; a total of a given number of coins was lost.
# Find how many bags were stolen for each type of coin bag.
import mip


def build(instance):
    coin_numbers = instance["coin_numbers"]
    total = instance["total_coins_lost"]
    n = len(coin_numbers)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # the number of stolen bags of each type; a type cannot be stolen more often than
    # its coins fit in the total
    bags = [
        model.add_var(f"bags_{i}", lb=0, ub=total // coin_numbers[i], var_type=mip.INTEGER)
        for i in range(n)
    ]

    # a total of a given number of coins were lost
    model.add_constr(mip.xsum(coin_numbers[i] * bags[i] for i in range(n)) == total)

    return model, {"bags": bags}
