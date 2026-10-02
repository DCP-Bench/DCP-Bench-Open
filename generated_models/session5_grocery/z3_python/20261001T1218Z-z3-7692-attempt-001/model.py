# Grocery: a kid buys some items. The cashier multiplied the prices instead of adding them,
# and the product came to the same total price as the sum. Find the prices, in cents.
import z3


def build(instance):
    total_price = instance["total_price"]  # total price in cents
    num_items = instance["num_items"]

    # prices[i] is the price of item i, in cents, between 1 and the total price.
    prices = [z3.Int(f"prices_{i}") for i in range(num_items)]

    solver = z3.Solver()

    # The prices add up to the total price.
    solver.add(z3.Sum(prices) == total_price)

    # Their product, taken with the prices in dollars, equals the total price in dollars. In
    # cents the product is 100 times larger for every item beyond the first.
    product_target = total_price * 100 ** (num_items - 1)
    solver.add(z3.Product(prices) == product_target)

    # Every price is at least 1 cent, and (the others being at least 1 cent each) at most the
    # total price minus one cent for each other item.
    # Implied by the product equation: every price divides the product target, so it can only
    # be one of the divisors of the target below the upper bound. This cuts the search for the
    # nonlinear product to a few dozen values per item.
    upper = total_price - (num_items - 1)
    divisors = [d for d in range(1, max(upper, 1) + 1) if product_target % d == 0]
    for p in prices:
        solver.add(p >= 1, p <= total_price)
        solver.add(z3.Or([p == d for d in divisors]))

    return solver, {"prices": prices}
