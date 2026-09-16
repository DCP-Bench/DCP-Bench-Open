import pulp


def build(instance):
    """Equal sized groups: cut a sorted list into k groups as close as possible
    to the ideal size, without splitting a run of equal values.
    """
    a = instance["a"]
    k = instance["k"]
    n = len(a)
    gsize = round(n / k)

    problem = pulp.LpProblem("groups", pulp.LpMinimize)
    s = [pulp.LpVariable(f"s{i}", 1, n, cat="Integer") for i in range(k)]
    x = [pulp.LpVariable(f"x{i}", 1, n, cat="Integer") for i in range(k - 1)]

    problem += s[0] == x[0]
    for i in range(1, k - 1):
        problem += s[i] == x[i] - x[i - 1]
    problem += s[k - 1] == n - x[k - 2]

    # Under minimization the two bounds pin each absolute error.
    errors = []
    for i in range(k):
        error = pulp.LpVariable(f"e{i}", 0, n, cat="Integer")
        problem += error >= s[i] - gsize
        problem += error >= gsize - s[i]
        errors.append(error)
    problem += pulp.lpSum(errors)

    # Equal values stay together. The comparison is over instance data, so it
    # resolves here and only the real restrictions reach the model; a break
    # point is forbidden from sitting at j through a pair of big-M bounds.
    for j in range(1, n):
        if a[j - 1] != a[j]:
            continue
        for p in range(k - 1):
            below = pulp.LpVariable(f"below_{j}_{p}", cat="Binary")
            problem += x[p] <= j - 1 + n * (1 - below)
            problem += x[p] >= j + 1 - n * below

    return problem, {"x": x}
