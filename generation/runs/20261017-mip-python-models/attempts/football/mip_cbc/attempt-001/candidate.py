# Football: choose a squad from the listed players to spend as much as possible
# (at most GBP 30 million) and output the total price in GBP thousands (z).
# Prices are in GBP thousands (price in millions times 1000, exact integers).
import mip


GOALKEEPERS = [730, 1280, 3880]
DEFENDERS = [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570]
MIDFIELDERS = [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130]
STRIKERS = [4460, 6470, 7780, 8390, 9500]
LIMIT = 30000


def build(instance):
    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    g = [model.add_var(f"g{i + 1}", var_type=mip.BINARY) for i in range(len(GOALKEEPERS))]
    d = [model.add_var(f"d{i + 1}", var_type=mip.BINARY) for i in range(len(DEFENDERS))]
    m = [model.add_var(f"m{i + 1}", var_type=mip.BINARY) for i in range(len(MIDFIELDERS))]
    s = [model.add_var(f"s{i + 1}", var_type=mip.BINARY) for i in range(len(STRIKERS))]

    # Goalkeepers (must buy 1 exactly)
    model += mip.xsum(g) == 1

    # Defenders (must buy 2 or more)
    model += mip.xsum(d) >= 2

    # Midfielders (must buy 3 or more)
    model += mip.xsum(m) >= 3

    # Strikers (must buy 2 or more)
    model += mip.xsum(s) >= 2

    # Also, you must buy at least eleven players in total.
    model += mip.xsum(g + d + m + s) >= 11

    # The chairman gives you an upper limit of GBP 30 million, so the purchases
    # must not go over it.
    total_price = mip.xsum(
        [p * x for p, x in zip(GOALKEEPERS, g)]
        + [p * x for p, x in zip(DEFENDERS, d)]
        + [p * x for p, x in zip(MIDFIELDERS, m)]
        + [p * x for p, x in zip(STRIKERS, s)]
    )
    model += total_price <= LIMIT

    # Print out the total price of the players you have selected (z) in GBP
    # thousands.
    z = model.add_var("z", lb=0, ub=LIMIT, var_type=mip.INTEGER)
    model += z == total_price

    # Spend as much money as you can.
    model.objective = z

    return model, {"z": z}
