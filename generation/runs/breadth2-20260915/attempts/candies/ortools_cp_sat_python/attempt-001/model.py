from ortools.sat.python import cp_model


def build(instance):
    ratings = instance["ratings"]
    n = len(ratings)
    model = cp_model.CpModel()
    candies = [model.new_int_var(1, n, f"x_{i}") for i in range(n)]
    total = model.new_int_var(1, n * n, "z")
    model.add(total == sum(candies))
    model.add(total >= n)
    for i in range(1, n):
        if ratings[i - 1] > ratings[i]:
            model.add(candies[i - 1] > candies[i])
        elif ratings[i - 1] < ratings[i]:
            model.add(candies[i - 1] < candies[i])
    model.minimize(total)
    return model, {"z": total, "x": candies}
