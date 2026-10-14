"""Grocery: a kid buys a number of items. The cashier multiplies the prices (in cents)
instead of adding them, and gets the same total as when adding them: the sum of the prices is
the total price, and the product of the prices, in euros, is the total price too. What are the
prices of the items?

The model reports the prices in cents.
"""
import pulp


def build(instance):
    total_price = instance["total_price"]  # total price in cents
    k = instance["num_items"]  # number of items

    # The product of the prices in cents is the total price in cents times 100 for each of the
    # k - 1 multiplications beyond the first (the total in euros is the product in euros).
    target = total_price * 100 ** (k - 1)

    problem = pulp.LpProblem("grocery", pulp.LpMinimize)  # satisfaction: no objective

    # A price is a whole number of cents from 1 to the total price. The product of the prices is
    # `target`, so every price divides `target`; only those divisors are possible prices.
    candidates = [v for v in range(1, total_price + 1) if target % v == 0]

    # pick[i][v] = 1 if item i costs v cents; an item has exactly one price
    pick = pulp.LpVariable.dicts("pick", (range(k), candidates), cat="Binary")
    prices = [pulp.LpVariable(f"price_{i}", 1, total_price, cat="Integer") for i in range(k)]
    for i in range(k):
        problem += pulp.lpSum(pick[i][v] for v in candidates) == 1
        problem += prices[i] == pulp.lpSum(v * pick[i][v] for v in candidates)

    # the prices add up to the total price
    problem += pulp.lpSum(prices) == total_price

    # The prices multiply to `target`. A product is not linear, but whole numbers are equal
    # exactly when every prime occurs equally often in them. Every prime of `target` must occur
    # in the prices as often as in `target` (a prime factor of `target` is a prime factor of the
    # price it belongs to, and a price has no other prime factors since it divides `target`).
    def exponent(p, number):
        """how many times the prime p divides number"""
        count = 0
        while number % p == 0:
            number //= p
            count += 1
        return count

    primes = []
    rest = target
    p = 2
    while rest > 1:
        if rest % p == 0:
            primes.append(p)
            while rest % p == 0:
                rest //= p
        p += 1
    for p in primes:
        problem += pulp.lpSum(exponent(p, v) * pick[i][v]
                              for i in range(k) for v in candidates) == exponent(p, target)

    return problem, {"prices": prices}
