# Grocery puzzle: a kid buys num_items items and the cashier charges total_price (in cents).
# The cashier multiplied the item prices instead of adding them, and the product also
# comes to total_price. Find the prices (positive whole numbers of cents) whose sum and
# whose product both equal total_price. Output: prices, one integer per item.
import mip


def _prime_exponents(n):
    exps = {}
    q = 2
    while q * q <= n:
        while n % q == 0:
            exps[q] = exps.get(q, 0) + 1
            n //= q
        q += 1
    if n > 1:
        exps[n] = exps.get(n, 0) + 1
    return exps


def build(instance):
    n = instance["num_items"]
    total = instance["total_price"]
    model = mip.Model(solver_name="CBC")

    # Each price is a positive whole number of cents, at most the total price, since the
    # prices add up to the total price. Each price divides the product of the prices.
    # The product of the prices is measured in cents: the prices are cents, so their
    # product is worth total_price * 100^(num_items - 1) in cents^n.
    product = total * 100 ** (n - 1)
    product_exps = _prime_exponents(product)
    divisors = [d for d in range(1, total + 1) if product % d == 0]
    exps = {d: _prime_exponents(d) for d in divisors}

    # One binary per item and per divisor: which value the item's price takes.
    pick = [
        {d: model.add_var(name=f"pick_{i}_{d}", var_type=mip.BINARY) for d in divisors}
        for i in range(n)
    ]
    price = [mip.xsum(d * pick[i][d] for d in divisors) for i in range(n)]

    # Each item takes exactly one price.
    for i in range(n):
        model.add_constr(mip.xsum(pick[i][d] for d in divisors) == 1)

    # The cashier charges a total price: the item prices add up to the total price.
    model.add_constr(mip.xsum(price) == total)

    # The cashier multiplied the items: the product of the prices, in cents, equals the
    # total price. With every price a divisor of that product, this holds exactly when,
    # for each prime, the prime exponents of the prices add up to the prime exponent of
    # the product.
    for q, target in product_exps.items():
        model.add_constr(
            mip.xsum(
                exps[d].get(q, 0) * pick[i][d]
                for i in range(n)
                for d in divisors
            )
            == target
        )

    return model, {"prices": price}
