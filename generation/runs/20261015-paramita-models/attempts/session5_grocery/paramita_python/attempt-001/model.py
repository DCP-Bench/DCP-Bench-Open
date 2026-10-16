# Grocery: a kid buys num_items items and the cashier charges total_price cents.
# Find item prices (cents) whose sum and whose product (in dollars) both equal total_price.
from paramita.modelling import Bool, If


def divisors(m):
    small, large = [], []
    d = 1
    while d * d <= m:
        if m % d == 0:
            small.append(d)
            if d * d != m:
                large.append(m // d)
        d += 1
    return small + large[::-1]


def build(instance):
    n, total = instance["num_items"], instance["total_price"]

    # Prices are in cents, the product is in dollars: prod(prices) / 100**(n-1)
    # equals total_price, so prod(prices) = total_price * 100**(n-1) = M.
    # Every price divides M, and every price is at most total_price because the
    # prices add up to total_price. These bounds give the candidate prices.
    M = total * 100 ** (n - 1)
    divisors_of_M = divisors(M)
    prices_domain = [d for d in divisors_of_M if d <= total]
    divisor_set = set(divisors_of_M)

    # Item i is one-hot over the candidate prices: p[i][d] means item i costs d cents.
    p = [{d: Bool(f"item_{i}_costs_{d}") for d in prices_domain} for i in range(n)]

    cons = []
    # every item has exactly one price
    cons += [sum(p[i].values()) == 1 for i in range(n)]

    # adding the items gives the total price
    cons += [sum(d * p[i][d] for i in range(n) for d in prices_domain) == total]

    # multiplying the items (in dollars) gives the same total price. r[j][e] means
    # the product of the first j prices is e; only divisors of M can occur.
    # The state after the first item is the item's own price.
    r = {1: dict(p[0])}
    for j in range(2, n + 1):
        prev = r[j - 1]
        cur = {e: Bool(f"product_of_first_{j}_items_is_{e}") for e in divisor_set}
        r[j] = cur
        # exactly one product for the first j items
        cons.append(sum(cur.values()) == 1)
        for e0 in prev:
            for d in prices_domain:
                e = e0 * d
                if e in divisor_set:
                    # the first j-1 items multiply to e0 and item j-1 costs d: product e0*d
                    cons.append(If(prev[e0] & p[j - 1][d], cur[e]))
                else:
                    # a product that does not divide M cannot lead to M
                    cons.append(~(prev[e0] & p[j - 1][d]))

    # the product of all items is total_price * 100**(n-1)
    cons.append(r[n][M])

    # the prices, in cents
    prices = [sum(d * p[i][d] for d in prices_domain) for i in range(n)]

    return cons, {"prices": prices}
