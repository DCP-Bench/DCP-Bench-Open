from pyscipopt import Model, quicksum

# Football squad selection: choose players from the groups of goalkeepers, defenders,
# midfielders and strikers, spending as much as possible without going over GBP 30 million.
# The prices are fixed by the problem statement, so they are written here.
# Prices are in GBP millions in the statement; the objective uses GBP thousands (price * 1000).
def build(instance):
    # price of each player in GBP thousands, grouped by position
    goalkeepers = {"g1": 0.73, "g2": 1.28, "g3": 3.88}
    defenders = {"d1": 0.92, "d2": 1.31, "d3": 1.62, "d4": 2.41,
                 "d5": 2.79, "d6": 3.28, "d7": 3.91, "d8": 4.57}
    midfielders = {"m1": 1.8, "m2": 2.63, "m3": 3.17, "m4": 3.769, "m5": 4.14,
                   "m6": 4.75, "m7": 5.38, "m8": 5.93, "m9": 6.78, "m10": 7.13}
    strikers = {"s1": 4.46, "s2": 6.47, "s3": 7.78, "s4": 8.39, "s5": 9.5}

    m = Model()

    # buy[p] = 1 if player p is bought (each player is bought at most once)
    groups = {"goalkeeper": goalkeepers, "defender": defenders,
              "midfielder": midfielders, "striker": strikers}
    buy = {}
    for group, players in groups.items():
        for p in players:
            buy[p] = m.addVar(name=f"buy_{p}", vtype="B")

    # the budget: the purchases add up to at most GBP 30 million (30000 thousands)
    m.addCons(quicksum(round(price * 1000) * buy[p]
                       for players in groups.values()
                       for p, price in players.items()) <= 30000)

    # must buy exactly 1 goalkeeper
    m.addCons(quicksum(buy[p] for p in goalkeepers) == 1)
    # must buy 2 or more defenders
    m.addCons(quicksum(buy[p] for p in defenders) >= 2)
    # must buy 3 or more midfielders
    m.addCons(quicksum(buy[p] for p in midfielders) >= 3)
    # must buy 2 or more strikers
    m.addCons(quicksum(buy[p] for p in strikers) >= 2)
    # must buy at least eleven players in total
    m.addCons(quicksum(buy[p] for p in buy) >= 11)

    # z = total price of the selected players in GBP thousands
    z = m.addVar(name="z", vtype="I", lb=0, ub=30000)
    m.addCons(z == quicksum(round(price * 1000) * buy[p]
                            for players in groups.values()
                            for p, price in players.items()))

    # spend as much of the GBP 30 million as possible
    m.setObjective(z, "maximize")
    return m, {"z": z}
