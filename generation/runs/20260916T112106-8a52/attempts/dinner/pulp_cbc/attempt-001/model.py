import pulp


def build(instance):
    """Dinner: twenty people for twenty dollars, prices doubled through so the
    fifty-cent child stays an integer.
    """
    del instance

    problem = pulp.LpProblem("dinner", pulp.LpMinimize)
    grandparents = pulp.LpVariable("grandparents", 1, 6, cat="Integer")
    parents = pulp.LpVariable("parents", 1, 10, cat="Integer")
    children = pulp.LpVariable("children", 1, 40, cat="Integer")

    problem += 6 * grandparents + 4 * parents + children == 40
    problem += grandparents + parents + children == 20

    return problem, {
        "grandparents": grandparents, "parents": parents, "children": children,
    }
