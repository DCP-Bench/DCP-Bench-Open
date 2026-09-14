import pulp


def build(instance):
    ratings = instance["ratings"]
    n = len(ratings)
    problem = pulp.LpProblem("candies", pulp.LpMinimize)
    candies = [pulp.LpVariable(f"x_{i}", 1, n, cat="Integer") for i in range(n)]
    total = pulp.LpVariable("z", 1, n * n, cat="Integer")
    problem += total == pulp.lpSum(candies)
    problem += total >= n
    for i in range(1, n):
        # Strict inequalities over integers are the same shifted by one.
        if ratings[i - 1] > ratings[i]:
            problem += candies[i - 1] >= candies[i] + 1
        elif ratings[i - 1] < ratings[i]:
            problem += candies[i - 1] + 1 <= candies[i]
    problem += total
    return problem, {"z": total, "x": candies}
