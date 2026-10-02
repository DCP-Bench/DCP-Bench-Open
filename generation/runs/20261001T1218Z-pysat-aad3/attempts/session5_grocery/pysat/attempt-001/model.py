# Grocery: the prices (in cents) of the items a kid bought add up to the total price, and their
# product, read as a price in the same way, equals the total price too. Multiplying the prices
# in cents gives total_price * 100^(num_items - 1) once the cents are scaled back to euros.
from pysat.formula import IDPool
from pysat.pb import PBEnc
from pysat.integer import Integer, IntegerEngine


def divisors(value):
    """All divisors of value, by trial division up to its square root."""
    found = set()
    d = 1
    while d * d <= value:
        if value % d == 0:
            found.update((d, value // d))
        d += 1
    return sorted(found)


def build(instance):
    total_price = instance["total_price"]  # in cents
    m = instance["num_items"]

    # the product of the prices has to equal this number (the reference's scaled total price)
    target = total_price * 100 ** (m - 1)

    pool = IDPool()
    # prices[k] = price of item k in cents, between 1 and the total price
    prices = [Integer(f"price{k}", 1, total_price, vpool=pool) for k in range(m)]
    engine = IntegerEngine(vars=prices, vpool=pool)
    cnf = engine.clausify()

    # Every price divides the target, since the prices multiply to it, and so does every partial
    # product. A price that does not divide it is ruled out; this keeps the encodings below small
    # (the target is large, so a one-hot product over 1..target would not fit).
    divs = divisors(target)
    allowed = [v for v in divs if v <= total_price]
    for item in prices:
        for value in range(1, total_price + 1):
            if target % value != 0:
                cnf.append([-item.equals(value)])

    # the prices add up to the total price (only the values that can occur are counted)
    lits = [item.equals(v) for item in prices for v in allowed]
    weights = [v for _ in prices for v in allowed]
    cnf.extend(PBEnc.equals(lits=lits, weights=weights, bound=total_price, vpool=pool).clauses)

    # the prices multiply to the target. partial[d] says "the product of the prices so far is d";
    # each item multiplies the previous partial product by its price, and a product that no longer
    # divides the target is excluded.
    partial = {v: prices[0].equals(v) for v in allowed}
    for k in range(1, m):
        following = {d: pool.id(("product", k, d)) for d in divs}
        for d, so_far in partial.items():
            for v in allowed:
                if target % (d * v) == 0:
                    cnf.append([-so_far, -prices[k].equals(v), following[d * v]])
                else:
                    cnf.append([-so_far, -prices[k].equals(v)])
        partial = following
    for d, product in partial.items():
        if d != target:
            cnf.append([-product])

    return cnf, {"prices": prices}
