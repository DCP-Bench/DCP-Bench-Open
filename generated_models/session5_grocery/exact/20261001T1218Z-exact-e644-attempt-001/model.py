# Grocery: the prices of a few items (in cents) add up to a total, and they also multiply to the
# same total (read in dollars). Find the prices.
from exact import Exact


def build(instance):
    total_price = instance["total_price"]  # total price in cents
    num_items = instance["num_items"]

    # the product of the prices in cents must equal the total price scaled by 100 for each
    # extra factor (the product is in dollars^num_items, the sum in dollars)
    target_product = total_price * 100 ** (num_items - 1)

    # Exact has no product of variables that scales well, so the product is stated through prime
    # exponents: a product of prices is target_product exactly when, for every prime p, the
    # exponents of p in the prices add up to the exponent of p in target_product. Each price
    # divides target_product, which restricts it to a short list of divisors.
    primes = {2, 5}  # the primes of 100
    rest, q = total_price, 2
    while q * q <= rest:
        while rest % q == 0:
            primes.add(q)
            rest //= q
        q += 1
    if rest > 1:
        primes.add(rest)

    def exponent(value, p):
        count = 0
        while value % p == 0:
            value //= p
            count += 1
        return count

    # prices are between 1 and total_price and divide the target product
    candidates = [d for d in range(1, total_price + 1) if target_product % d == 0]

    solver = Exact()

    # prices[i] = price of item i; chosen[i][k] = 1 when item i costs candidates[k]
    prices = [f"price_{i}" for i in range(num_items)]
    chosen = [[f"price_{i}_is_{d}" for d in candidates] for i in range(num_items)]
    for i in range(num_items):
        solver.addVariable(prices[i], 1, total_price)
        for name in chosen[i]:
            solver.addVariable(name, 0, 1)
        solver.addConstraint([(1, name) for name in chosen[i]], True, 1, True, 1)
        solver.addConstraint([(d, chosen[i][k]) for k, d in enumerate(candidates)]
                             + [(-1, prices[i])], True, 0, True, 0)

    # the sum of the prices in cents is equal to the total price
    solver.addConstraint([(1, name) for name in prices], True, total_price, True, total_price)

    # the product of the prices equals the target product, prime by prime
    for p in sorted(primes):
        target = exponent(target_product, p)
        solver.addConstraint(
            [(exponent(d, p), chosen[i][k]) for i in range(num_items)
             for k, d in enumerate(candidates) if exponent(d, p)],
            True, target, True, target)

    return solver, {"prices": prices}
