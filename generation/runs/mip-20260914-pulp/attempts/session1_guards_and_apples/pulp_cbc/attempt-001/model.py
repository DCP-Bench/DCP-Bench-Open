import pulp


def build(instance):
    gates = instance["num_gates"]
    problem = pulp.LpProblem("guards_and_apples", pulp.LpMinimize)
    apples = [pulp.LpVariable(f"apples_{i}", 0, 100, cat="Integer") for i in range(gates + 1)]
    problem += apples[gates] == 1
    for i in range(1, gates + 1):
        problem += apples[i - 1] == 2 * (apples[i] + 1)
    return problem, {"apples": apples}
