from pychoco.model import Model


def build(instance):
    """Subset sum: how many bags of each coin type were stolen, given the total
    number of coins lost.
    """
    total = instance["total_coins_lost"]
    coins = instance["coin_numbers"]
    n = len(coins)

    model = Model()
    bags = [model.intvar(0, total, name=f"b{i}") for i in range(n)]

    model.scalar(bags, coins, "=", total).post()

    return model, {"bags": bags}
