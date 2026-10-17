# Football: choose players to buy for a Premiership squad, maximising the total
# price spent without going over the GBP 30 million limit. Prices are in GBP
# thousands, so the output z is the total price in GBP thousands.
import cvc5.pythonic as cz

GOALKEEPERS = [730, 1280, 3880]
DEFENDERS = [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570]
MIDFIELDERS = [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130]
STRIKERS = [4460, 6470, 7780, 8390, 9500]


def build(instance):
    # Each player is bought at most once: one Boolean per player.
    gk = [cz.Bool(f"gk_{i}") for i in range(len(GOALKEEPERS))]
    df = [cz.Bool(f"df_{i}") for i in range(len(DEFENDERS))]
    md = [cz.Bool(f"md_{i}") for i in range(len(MIDFIELDERS))]
    st = [cz.Bool(f"st_{i}") for i in range(len(STRIKERS))]
    groups = [
        (gk, GOALKEEPERS),
        (df, DEFENDERS),
        (md, MIDFIELDERS),
        (st, STRIKERS),
    ]

    z = cz.Int("z")
    constraints = [z >= 0]

    # Goalkeepers: must buy exactly 1.
    constraints.append(cz.Sum([cz.If(b, 1, 0) for b in gk]) == 1)
    # Defenders: must buy 2 or more.
    constraints.append(cz.Sum([cz.If(b, 1, 0) for b in df]) >= 2)
    # Midfielders: must buy 3 or more.
    constraints.append(cz.Sum([cz.If(b, 1, 0) for b in md]) >= 3)
    # Strikers: must buy 2 or more.
    constraints.append(cz.Sum([cz.If(b, 1, 0) for b in st]) >= 2)
    # Also, you must buy at least eleven players in total.
    players = [b for group, _ in groups for b in group]
    constraints.append(cz.Sum([cz.If(b, 1, 0) for b in players]) >= 11)

    # The total price is z; it is at most the GBP 30 million limit.
    prices = [
        cz.If(b, p, 0)
        for group, group_prices in groups
        for b, p in zip(group, group_prices)
    ]
    constraints.append(z == cz.Sum(prices))
    constraints.append(z <= 30000)

    outputs = {"z": z}
    return constraints, outputs, ("maximize", z)
