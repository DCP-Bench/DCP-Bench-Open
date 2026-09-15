import z3


def build(instance):
    total, items = instance["total_price"], instance["num_items"]
    prices = [z3.Int(f"p_{i}") for i in range(items)]
    constraints = [p >= 1 for p in prices] + [p <= total for p in prices]
    constraints.append(z3.Sum(prices) == total)
    product = prices[0]
    for i in range(1, items):
        product = product * prices[i]
    constraints.append(product == total * 100 ** (items - 1))
    return constraints, {"prices": prices}
