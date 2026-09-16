import pulp


def build(instance):
    """Farmer and cows: split the herd between the sons so that each gets his
    allotted number of cows and exactly the same amount of milk.
    """
    num_cows = instance["num_cows"]
    num_sons = instance["num_sons"]
    cows_per_son = instance["cows_per_son"]

    # Cow i yields i + 1 units of milk, as the reference lays the herd out.
    milk = [i + 1 for i in range(num_cows)]
    share = sum(milk) // num_sons

    problem = pulp.LpProblem("farmer", pulp.LpMinimize)
    # gets[i][s] says cow i went to son s.
    gets = pulp.LpVariable.dicts("gets", (range(num_cows), range(num_sons)), cat="Binary")

    for i in range(num_cows):
        problem += pulp.lpSum(gets[i][s] for s in range(num_sons)) == 1
    for s in range(num_sons):
        problem += pulp.lpSum(gets[i][s] for i in range(num_cows)) == cows_per_son[s]
        problem += pulp.lpSum(milk[i] * gets[i][s] for i in range(num_cows)) == share

    assignments = [pulp.LpVariable(f"a{i}", 0, num_sons - 1, cat="Integer")
                   for i in range(num_cows)]
    for i in range(num_cows):
        problem += assignments[i] == pulp.lpSum(s * gets[i][s] for s in range(num_sons))

    return problem, {"cow_assignments": assignments}
