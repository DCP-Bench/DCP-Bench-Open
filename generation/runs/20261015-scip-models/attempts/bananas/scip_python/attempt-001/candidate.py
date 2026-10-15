# Bananas: buy 100 fruits for 100 dollars, at least one of each kind,
# minimising the number of bananas and apples.
from pyscipopt import Model, quicksum


def build(instance):
    m = Model()
    # quantities bought, in the order of the output names
    apples = m.addVar(name="apples", vtype="I", lb=1, ub=100)
    bananas = m.addVar(name="bananas", vtype="I", lb=1, ub=100)
    mangoes = m.addVar(name="mangoes", vtype="I", lb=1, ub=100)
    oranges = m.addVar(name="oranges", vtype="I", lb=1, ub=100)

    # 100 fruits in total
    m.addCons(apples + bananas + mangoes + oranges == 100)

    # 100 dollars in total. Prices from the statement: 5 bananas for 3 dollars,
    # 7 oranges for 5, 9 mangoes for 7, 3 apples for 9. Multiplied by 315
    # (the least common multiple of 5, 7, 9 and 3) so all coefficients are integers:
    # bananas 189, oranges 225, mangoes 245, apples 945, total 31500.
    m.addCons(189 * bananas + 225 * oranges + 245 * mangoes + 945 * apples == 31500)

    # bananas and apples should be bought in minimum quantity
    m.setObjective(bananas + apples, "minimize")

    return m, {
        "apples": apples,
        "bananas": bananas,
        "mangoes": mangoes,
        "oranges": oranges,
    }
