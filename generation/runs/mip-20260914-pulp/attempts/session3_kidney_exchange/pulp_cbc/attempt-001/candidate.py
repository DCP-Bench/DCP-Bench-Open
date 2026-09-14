import pulp


def build(instance):
    count = instance["num_people"]
    compatible = instance["compatible"]
    people = range(count)
    problem = pulp.LpProblem("kidney_exchange", pulp.LpMaximize)
    donates = [[pulp.LpVariable(f"t_{i}_{j}", cat="Binary") for j in people] for i in people]
    for i in people:
        gives = pulp.lpSum(donates[i])
        receives = pulp.lpSum(donates[k][i] for k in people)
        problem += gives <= 1
        problem += receives <= 1
        # Donating implies receiving; both sums are 0 or 1 by the constraints above.
        problem += gives <= receives
        for j in people:
            if j + 1 not in compatible[i]:
                problem += donates[i][j] == 0
    problem += pulp.lpSum(donates[i][j] for i in people for j in people)
    return problem, {"transplants": donates}
