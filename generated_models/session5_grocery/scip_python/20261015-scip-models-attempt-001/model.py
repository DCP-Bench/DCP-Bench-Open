# Grocery: find item prices (in cents) whose sum is the total and whose product, in dollars, is the total.
from pyscipopt import Model, quicksum


def build(instance):
    num_items = instance["num_items"]
    total = instance["total_price"]
    m = Model()

    # prices[i] = price of item i in cents; a price is at least 1 cent and at most the total
    # (the prices add up to the total and each one is at least 1 cent)
    prices = [m.addVar(name=f"price_{i}", vtype="I", lb=1, ub=total) for i in range(num_items)]

    # the cashier's sum: adding the item prices gives the total price (in cents)
    m.addCons(quicksum(prices) == total)

    # the cashier's mistake: multiplying the item prices gives the same total. Each price is in cents,
    # so the product of the prices is divided by 100 once per factor after the first (in dollars),
    # i.e. prod(prices) == total * 100**(num_items - 1). Checked against the examples: 200 * 200 / 100 = 400.
    # SCIP has no product over a list, so the running product is kept in prod[i]. Every prefix product
    # is at least 1 and at most the full product, since all factors are at least 1.
    full = total * 100 ** (num_items - 1)
    prod = [m.addVar(name=f"prod_{i}", vtype="I", lb=1, ub=full) for i in range(num_items)]
    m.addCons(prod[0] == prices[0])
    for i in range(1, num_items):
        m.addCons(prod[i] == prod[i - 1] * prices[i])
    m.addCons(prod[num_items - 1] == full)

    return m, {"prices": prices}
