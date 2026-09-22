# How many bags of each coin type were stolen, given the total coins lost.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    coin_numbers = instance["coin_numbers"]
    total = instance["total_coins_lost"]

    pool = IDPool()
    # No bag type can appear more often than the total allows, which keeps the
    # domain encoding to the values that can actually occur.
    bags = [Integer(f"bag{i}", 0, total // value if value else total, vpool=pool)
            for i, value in enumerate(coin_numbers)]
    engine = IntegerEngine(vars=bags, vpool=pool)
    engine.add_linear(sum(coin_numbers[i] * bags[i]
                          for i in range(len(coin_numbers))) == total)
    return engine.clausify(), {"bags": bags}
