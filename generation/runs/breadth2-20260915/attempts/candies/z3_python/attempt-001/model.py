import z3


def build(instance):
    ratings = instance["ratings"]
    n = len(ratings)
    candies = [z3.Int(f"x_{i}") for i in range(n)]
    total = z3.Int("z")
    constraints = [c >= 1 for c in candies] + [c <= n for c in candies]
    constraints += [total == z3.Sum(candies), total >= n, total <= n * n]
    for i in range(1, n):
        if ratings[i - 1] > ratings[i]:
            constraints.append(candies[i - 1] > candies[i])
        elif ratings[i - 1] < ratings[i]:
            constraints.append(candies[i - 1] < candies[i])
    return constraints, {"z": total, "x": candies}, ("minimize", total)
