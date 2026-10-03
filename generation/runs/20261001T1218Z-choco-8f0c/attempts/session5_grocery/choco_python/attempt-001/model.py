# Grocery: a kid buys some items. The cashier multiplied the prices instead of adding
# them, and the product (read in dollars) came out equal to the sum. Find the prices,
# in cents, of the items.
from pychoco.model import Model


def build(instance):
    total_price = instance["total_price"]  # total price in cents
    num_items = instance["num_items"]

    model = Model()

    # prices[i] = price of item i in cents, between 1 and the total price
    prices = [model.intvar(1, total_price, name=f"prices_{i}") for i in range(num_items)]

    # the sum of the prices in cents is the total price
    model.sum(prices, "=", total_price).post()

    # the product of the prices in cents is the total price scaled to cents^num_items,
    # i.e. total_price * 100^(num_items - 1). The product is built up one item at a
    # time. As every price is at least 1, every partial product is at most the full
    # product, which keeps all partial products within Choco's integer range.
    product_target = total_price * 100 ** (num_items - 1)
    partial = prices[0]
    for i in range(1, num_items):
        if i == num_items - 1:
            next_partial = model.intvar(product_target, product_target, name="product")
        else:
            next_partial = model.intvar(1, product_target, name=f"partial_product_{i}", bounded_domain=True)
        model.times(partial, prices[i], next_partial).post()
        partial = next_partial
    if num_items == 1:
        model.arithm(prices[0], "=", product_target).post()

    return model, {"prices": prices}
