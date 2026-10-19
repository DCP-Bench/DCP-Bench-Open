# Grocery store: a kid buys num_items items; the cashier charges total_price (cents).
# The cashier multiplied the item prices instead of adding them, and the product
# comes to the same total as the sum. Find the item prices (cents).
# Prices are in cents; the product is taken in dollars (each price divided by 100),
# so the product of the cent prices equals total_price * 100^(num_items - 1).
from cvc5.pythonic import BitVec, BV2Int, Int, ZeroExt


def build(instance):
    n = instance["num_items"]
    total = instance["total_price"]
    product_total = total * 100 ** (n - 1)

    # Width of the bit-vectors: every partial product is at most product_total,
    # so one more bit than product_total needs is enough for each factor.
    width = product_total.bit_length() + 1

    # Prices are positive amounts in cents, and none can exceed the total.
    prices = [Int(f"p{i}") for i in range(n)]
    bits = [BitVec(f"x{i}", width) for i in range(n)]

    constraints = []
    for p, x in zip(prices, bits):
        constraints.append(p >= 1)
        constraints.append(p <= total)
        constraints.append(p == BV2Int(x, is_signed=False))

    # Adding the items gives the total price. The sum is taken on bit-vectors
    # wide enough for n prices, so it cannot wrap.
    extra = max(1, n.bit_length())
    total_sum = ZeroExt(extra, bits[0])
    for x in bits[1:]:
        total_sum = total_sum + ZeroExt(extra, x)
    constraints.append(total_sum == total)

    # Multiplying the items (in dollars) also gives the total price.
    # Each product is computed on bit-vectors twice as wide, so it cannot wrap.
    acc = bits[0]
    for i in range(1, n):
        nxt = BitVec(f"a{i}", width)
        constraints.append(ZeroExt(width, acc) * ZeroExt(width, bits[i]) == ZeroExt(width, nxt))
        acc = nxt
    constraints.append(acc == product_total)

    return constraints, {"prices": prices}
