import cpmpy as cp


def build(instance):
    amount, types, available = (instance["amount"], instance["types_of_coins"],
                                instance["available_coins"])
    n = len(types)
    counts = cp.intvar(0, max(available), shape=n, name="coin_counts")
    model = cp.Model(cp.sum([counts[i] * types[i] for i in range(n)]) == amount)
    for i in range(n):
        model += counts[i] <= available[i]
    model.minimize(cp.sum([counts[i] for i in range(n)]))
    return model, {"coin_counts": [counts[i] for i in range(n)]}
