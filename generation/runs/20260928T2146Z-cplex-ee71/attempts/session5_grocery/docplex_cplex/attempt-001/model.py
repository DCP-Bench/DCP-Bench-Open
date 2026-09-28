"""Grocery: find item prices in cents whose sum and whose product (read as dollars) give the same total."""
from docplex.mp.model import Model


def factorise(number):
    """The prime factorisation of a positive integer, as {prime: exponent}."""
    factors, prime = {}, 2
    while prime * prime <= number:
        while number % prime == 0:
            factors[prime] = factors.get(prime, 0) + 1
            number //= prime
        prime += 1
    if number > 1:
        factors[number] = factors.get(number, 0) + 1
    return factors


def build(instance):
    total, count = instance["total_price"], instance["num_items"]
    items = range(count)
    # Multiplying prices in cents gives cents to the power count, so the product
    # has to equal the total scaled by 100 for every factor after the first.
    product = total * 100 ** (count - 1)

    # The product of positive integers equals `product` exactly when each of them
    # divides it and, for every prime, their exponents add up to its exponent.
    # That turns the product into linear constraints over the divisors; CPLEX
    # would refuse the product itself as a non-convex constraint.
    primes = factorise(product)
    divisors = [d for d in range(1, total + 1) if product % d == 0]  # prices are 1..total
    exponent = {d: factorise(d) for d in divisors}

    model = Model("grocery")

    # costs[i, d] is 1 when item i costs d cents.
    costs = model.binary_var_matrix(items, divisors, name="costs")
    for i in items:
        model.add_constraint(model.sum(costs[i, d] for d in divisors) == 1, ctname=f"one_price_{i}")

    # Adding the prices gives the total.
    model.add_constraint(model.sum(d * costs[i, d] for i in items for d in divisors) == total, ctname="sum")

    # Multiplying the prices gives the scaled total, prime by prime.
    for p, power in primes.items():
        model.add_constraint(model.sum(exponent[d].get(p, 0) * costs[i, d] for i in items for d in divisors)
                             == power, ctname=f"product_{p}")

    return model, {"prices": [model.sum(d * costs[i, d] for d in divisors) for i in items]}
