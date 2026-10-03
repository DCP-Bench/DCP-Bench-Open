"""Football: buy a squad that spends as much of the GBP 30 million budget as possible without going over."""
import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data; prices (GBP thousands), budget and squad
# rules are the ones in the statement.
BUDGET = 30000
PRICES = {
    "goalkeeper": [730, 1280, 3880],
    "defender": [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570],
    "midfielder": [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130],
    "striker": [4460, 6470, 7780, 8390, 9500],
}
# How many of each type must be bought: (at least, at most).
COUNT = {"goalkeeper": (1, 1), "defender": (2, None), "midfielder": (3, None), "striker": (2, None)}
MIN_SQUAD = 11


def build(instance):
    model = gp.Model("football")

    # buy[t, j] = 1 when player j of type t is bought.
    buy = {(t, j): model.addVar(vtype=GRB.BINARY, name=f"buy[{t},{j}]")
           for t, prices in PRICES.items() for j in range(len(prices))}

    # Exactly one goalkeeper, two or more defenders, three or more midfielders,
    # two or more strikers.
    for t, (low, high) in COUNT.items():
        bought = gp.quicksum(buy[t, j] for j in range(len(PRICES[t])))
        model.addConstr(bought >= low, name=f"at_least[{t}]")
        if high is not None:
            model.addConstr(bought <= high, name=f"at_most[{t}]")

    # At least eleven players in total.
    model.addConstr(gp.quicksum(buy.values()) >= MIN_SQUAD, name="squad_size")

    # z is the total price, which must not go over the budget.
    z = model.addVar(lb=0, ub=BUDGET, vtype=GRB.INTEGER, name="z")
    model.addConstr(z == gp.quicksum(PRICES[t][j] * buy[t, j] for t, j in buy), name="total_price")

    # Spend as close to the budget as possible.
    model.setObjective(z, GRB.MAXIMIZE)

    return model, {"z": z}
