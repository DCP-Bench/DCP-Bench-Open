import pulp


def build(instance):
    """Just forgotten: recover a permutation of the digits, given several
    guesses that each got the same number of positions right.
    """
    sets = instance["sets"]
    num_correct = instance["num_correct_digits"]
    n = len(sets[0]) if sets else 0

    problem = pulp.LpProblem("just_forgotten", pulp.LpMinimize)
    # pick[i][d] says position i holds digit d; the row and column sums make
    # that a permutation, which is how all-different is written in a MIP.
    pick = pulp.LpVariable.dicts("pick", (range(n), range(n)), cat="Binary")
    for i in range(n):
        problem += pulp.lpSum(pick[i][d] for d in range(n)) == 1
    for d in range(n):
        problem += pulp.lpSum(pick[i][d] for i in range(n)) == 1

    # A guess scores one for each position where its digit was picked.
    for guess in sets:
        problem += pulp.lpSum(pick[i][guess[i]] for i in range(n)) == num_correct

    x = [pulp.LpVariable(f"x{i}", 0, n - 1, cat="Integer") for i in range(n)]
    for i in range(n):
        problem += x[i] == pulp.lpSum(d * pick[i][d] for d in range(n))

    return problem, {"x": x}
