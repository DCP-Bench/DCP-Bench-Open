import pulp


def build(instance):
    """Four numbers: find three values whose subsets sum to every given number.
    """
    numbers = instance["numbers"]
    m = len(numbers)
    n = 3
    upper = 10

    problem = pulp.LpProblem("four_numbers", pulp.LpMinimize)
    x = [pulp.LpVariable(f"x{j}", 1, upper, cat="Integer") for j in range(n)]

    for i in range(m):
        parts = []
        for j in range(n):
            chosen = pulp.LpVariable(f"c{i}_{j}", cat="Binary")
            # part is x[j] when chosen and zero otherwise, which is the linear
            # stand-in for the product of a binary and an integer.
            part = pulp.LpVariable(f"p{i}_{j}", 0, upper, cat="Integer")
            problem += part <= upper * chosen
            problem += part <= x[j]
            problem += part >= x[j] - upper * (1 - chosen)
            parts.append(part)
        problem += pulp.lpSum(parts) == numbers[i]

    return problem, {"x": x}
