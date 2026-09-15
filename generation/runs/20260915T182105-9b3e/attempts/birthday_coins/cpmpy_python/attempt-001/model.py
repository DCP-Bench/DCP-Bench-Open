import cpmpy as cp


def build(instance):
    """Birthday coins: fifteen old British coins worth one pound five and six.

    The puzzle states its own coinage, so `instance` is unused.  Working in
    pence: a half-crown is 30, a shilling 12, a sixpence 6, and the total is
    240 + 5 * 12 + 6.
    """
    del instance

    coin_types = 3
    values = [30, 12, 6]
    total_value = 240 + 5 * 12 + 6
    total_coins = 15

    coins = cp.intvar(0, 15, shape=coin_types, name="coins")
    half_crowns = coins[0]

    model = cp.Model(
        cp.sum(values[i] * coins[i] for i in range(coin_types)) == total_value,
        cp.sum(coins) == total_coins,
    )

    return model, {"half_crowns": half_crowns}
