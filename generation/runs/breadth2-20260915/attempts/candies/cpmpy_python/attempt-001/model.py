import cpmpy as cp


def build(instance):
    ratings = instance["ratings"]
    n = len(ratings)
    candies = cp.intvar(1, n, shape=n, name="x")
    total = cp.intvar(1, n * n, name="z")
    model = cp.Model(total == cp.sum([candies[i] for i in range(n)]), total >= n)
    for i in range(1, n):
        if ratings[i - 1] > ratings[i]:
            model += candies[i - 1] > candies[i]
        elif ratings[i - 1] < ratings[i]:
            model += candies[i - 1] < candies[i]
    model.minimize(total)
    return model, {"z": total, "x": [candies[i] for i in range(n)]}
