import pulp


def build(instance):
    """Eighteen hole golf: eighteen holes of length three, four or five that
    add up to a par of seventy-two.
    """
    del instance

    num_holes, total_length = 18, 72
    problem = pulp.LpProblem("golf", pulp.LpMinimize)
    holes = [pulp.LpVariable(f"h{i}", 3, 5, cat="Integer")
             for i in range(num_holes)]
    problem += pulp.lpSum(holes) == total_length

    return problem, {"holes": holes}
