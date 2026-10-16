# Football squad selection (Premiership). Each player is a Bool: bought or not.
# Prices are GBP thousands, so z is the total in thousands and the budget is 30000.
from paramita.modelling import Bool

GOALKEEPERS = [("g1", 730), ("g2", 1280), ("g3", 3880)]
DEFENDERS = [("d1", 920), ("d2", 1310), ("d3", 1620), ("d4", 2410),
             ("d5", 2790), ("d6", 3280), ("d7", 3910), ("d8", 4570)]
MIDFIELDERS = [("m1", 1800), ("m2", 2630), ("m3", 3170), ("m4", 3769), ("m5", 4140),
               ("m6", 4750), ("m7", 5380), ("m8", 5930), ("m9", 6780), ("m10", 7130)]
STRIKERS = [("s1", 4460), ("s2", 6470), ("s3", 7780), ("s4", 8390), ("s5", 9500)]


def build(instance):
    # Price table of the problem statement (GBP millions x 1000, so integers).
    groups = {"goalkeepers": GOALKEEPERS, "defenders": DEFENDERS,
              "midfielders": MIDFIELDERS, "strikers": STRIKERS}
    bought = {}
    for g, players in groups.items():
        for name, _ in players:
            bought[name] = Bool(f"bought_{name}")
    everyone = list(bought.values())

    def chosen(players):
        return [bought[name] for name, _ in players]

    cons = []
    # goalkeepers: buy exactly 1
    cons.append(sum(chosen(GOALKEEPERS)) == 1)
    # defenders: buy 2 or more
    cons.append(sum(chosen(DEFENDERS)) >= 2)
    # midfielders: buy 3 or more
    cons.append(sum(chosen(MIDFIELDERS)) >= 3)
    # strikers: buy 2 or more
    cons.append(sum(chosen(STRIKERS)) >= 2)
    # at least eleven players in total
    cons.append(sum(everyone) >= 11)

    # total price z of the bought players, in GBP thousands
    prices = [(bought[name], price) for players in groups.values() for name, price in players]
    z = sum(price * b for b, price in prices)
    # the chairman's limit: the purchases must not exceed GBP 30 million (30000 thousands)
    cons.append(z <= 30000)

    # maximise the money spent, as close to the limit as possible
    return cons, {"z": z}, ("maximize", z)
