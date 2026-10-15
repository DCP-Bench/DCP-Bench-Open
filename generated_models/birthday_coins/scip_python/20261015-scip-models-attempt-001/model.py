# Birthday coins: how many half-crowns were among 15 coins worth 1 pound 5 shillings 6 pence?
# Coin values in pence, from the problem statement: half-crown 30, shilling 12, sixpence 6.
# The instance has no fields, so every constant here comes from the problem statement.
from pyscipopt import Model


def build(instance):
    m = Model()
    half_crowns = m.addVar(name="half_crowns", vtype="I", lb=1, ub=13)
    shillings = m.addVar(name="shillings", vtype="I", lb=1, ub=13)
    sixpences = m.addVar(name="sixpences", vtype="I", lb=1, ub=13)

    # he was given 15 coins, of the three kinds named in the puzzle (each kind at least once)
    m.addCons(half_crowns + shillings + sixpences == 15)

    # the coins add up to 1 pound 5 shillings 6 pence, that is 306 pence
    m.addCons(30 * half_crowns + 12 * shillings + 6 * sixpences == 306)

    return m, {"half_crowns": half_crowns}
