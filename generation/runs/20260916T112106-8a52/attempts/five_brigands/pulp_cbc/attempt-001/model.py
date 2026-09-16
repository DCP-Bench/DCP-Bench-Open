import pulp


def build(instance):
    """Five brigands: 200 doubloons shared so that the reweighted shares also
    come to 200. Multiplying by six clears the halves and thirds.
    """
    del instance

    problem = pulp.LpProblem("brigands", pulp.LpMinimize)
    names = ["A", "B", "C", "D", "E"]
    x = {n: pulp.LpVariable(n, 1, 200, cat="Integer") for n in names}

    problem += pulp.lpSum(x.values()) == 200
    problem += (72 * x["A"] + 18 * x["B"] + 6 * x["C"]
                + 3 * x["D"] + 2 * x["E"] == 6 * 200)

    return problem, x
