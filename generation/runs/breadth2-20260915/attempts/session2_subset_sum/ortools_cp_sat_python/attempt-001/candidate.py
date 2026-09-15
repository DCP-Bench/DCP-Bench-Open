from ortools.sat.python import cp_model


def build(instance):
    total, coins = instance["total_coins_lost"], instance["coin_numbers"]
    model = cp_model.CpModel()
    bags = [model.new_int_var(0, total, f"bags_{i}") for i in range(len(coins))]
    model.add(sum(coins[i] * bags[i] for i in range(len(coins))) == total)
    return model, {"bags": bags}
