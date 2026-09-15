import cpmpy as cp


def build(instance):
    total, items = instance["total_price"], instance["num_items"]
    prices = cp.intvar(1, total, shape=items, name="prices")
    product = prices[0]
    for i in range(1, items):
        product = product * prices[i]
    model = cp.Model(cp.sum([prices[i] for i in range(items)]) == total,
                     product == total * 100 ** (items - 1))
    return model, {"prices": [prices[i] for i in range(items)]}
