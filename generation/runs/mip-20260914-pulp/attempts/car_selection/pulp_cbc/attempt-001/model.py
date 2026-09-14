import pulp


def build(instance):
    possible = instance["possible_assignments"]
    participants, cars = range(len(possible)), range(len(possible[0]))
    problem = pulp.LpProblem("car_selection", pulp.LpMaximize)
    assigned = [[pulp.LpVariable(f"a_{i}_{j}", cat="Binary") for j in cars] for i in participants]
    for i in participants:
        for j in cars:
            problem += assigned[i][j] <= possible[i][j]
        problem += pulp.lpSum(assigned[i]) <= 1
    for j in cars:
        problem += pulp.lpSum(assigned[i][j] for i in participants) <= 1
    problem += pulp.lpSum(assigned[i][j] for i in participants for j in cars)
    return problem, {"assignments": assigned}
