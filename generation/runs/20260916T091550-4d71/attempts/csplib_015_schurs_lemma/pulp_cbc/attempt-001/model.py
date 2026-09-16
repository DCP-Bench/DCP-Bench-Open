import pulp


def build(instance):
    """Schur's lemma: drop n balls into c boxes so that no box holds a triple
    x, y, z with x + y = z.
    """
    n = instance["n"]
    c = instance["c"]
    boxes = range(1, c + 1)

    problem = pulp.LpProblem("schur", pulp.LpMinimize)
    # in_box[i][b] says ball i + 1 is in box b.
    in_box = pulp.LpVariable.dicts("in_box", (range(n), boxes), cat="Binary")
    for i in range(n):
        problem += pulp.lpSum(in_box[i][b] for b in boxes) == 1

    # Ball labels are 1-based.  Forbidding all three of a triple from sharing a
    # box is exactly "at most two of the three indicators are on"; when x and y
    # are the same ball its indicator simply counts twice, which still says the
    # right thing.
    for x in range(1, n):
        for y in range(1, n - x + 1):
            z = x + y
            if z > n:
                continue
            for b in boxes:
                problem += in_box[x - 1][b] + in_box[y - 1][b] + in_box[z - 1][b] <= 2

    balls = [pulp.LpVariable(f"ball{i}", 1, c, cat="Integer") for i in range(n)]
    for i in range(n):
        problem += balls[i] == pulp.lpSum(b * in_box[i][b] for b in boxes)

    return problem, {"balls": balls}
