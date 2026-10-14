# Grocery: a kid buys some items. The cashier multiplied the prices instead of adding
# them, and the product (read in dollars) came out equal to the sum. Find the prices,
# in cents, of the items.
from pychoco.model import Model


def prime_factors(value):
    """Exponent of each prime in value, by trial division: {prime: exponent}."""
    factors = {}
    divisor = 2
    while divisor * divisor <= value:
        while value % divisor == 0:
            factors[divisor] = factors.get(divisor, 0) + 1
            value //= divisor
        divisor += 1
    if value > 1:
        factors[value] = factors.get(value, 0) + 1
    return factors


def build(instance):
    total_price = instance["total_price"]  # total price in cents
    num_items = instance["num_items"]

    model = Model()

    # prices[i] = price of item i in cents, between 1 and the total price
    prices = [model.intvar(1, total_price, name=f"prices_{i}") for i in range(num_items)]

    # the sum of the prices in cents is the total price
    model.sum(prices, "=", total_price).post()

    # The product of the prices in cents is the total price scaled to cents^num_items,
    # i.e. total_price * 100^(num_items - 1). That number is large (7.11e8 for the
    # example), and a chain of `times` constraints over it reports no solution, so the
    # product is stated through prime factors instead: every price divides the product,
    # and the product of the prices is the target exactly when, for each prime p, the
    # exponents of p in the prices add up to its exponent in the target. Only small
    # numbers are involved.
    product_target = total_price * 100 ** (num_items - 1)
    target_factors = prime_factors(product_target)
    primes = sorted(target_factors)

    # the possible prices: divisors of the target, each with the exponent of every prime
    tuples = []
    for price in range(1, total_price + 1):
        if product_target % price == 0:
            exponents = []
            rest = price
            for p in primes:
                e = 0
                while rest % p == 0:
                    rest //= p
                    e += 1
                exponents.append(e)
            tuples.append([price] + exponents)

    # exponents[i][k] = exponent of primes[k] in the price of item i, tied to the price by a table
    exponents = [[model.intvar(0, target_factors[p], name=f"exponent_{i}_{p}") for p in primes]
                 for i in range(num_items)]
    for i in range(num_items):
        model.table([prices[i]] + exponents[i], tuples).post()

    # for each prime, the exponents over all items add up to its exponent in the target
    for k, p in enumerate(primes):
        model.sum([exponents[i][k] for i in range(num_items)], "=", target_factors[p]).post()

    return model, {"prices": prices}
