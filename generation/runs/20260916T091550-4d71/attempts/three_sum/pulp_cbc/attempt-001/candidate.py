import pulp


def build(instance):
    """Three sum: pick exactly m of the numbers so that they add up to zero."""
    nums = instance["nums"]
    m = instance["m"]
    n = len(nums)

    problem = pulp.LpProblem("three_sum", pulp.LpMinimize)
    indices = [pulp.LpVariable(f"i{i}", cat="Binary") for i in range(n)]

    problem += pulp.lpSum(nums[i] * indices[i] for i in range(n)) == 0
    problem += pulp.lpSum(indices) == m

    return problem, {"indices": indices}
