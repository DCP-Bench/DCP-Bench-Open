import pulp


def build(instance):
    """Abbot puzzle: share 100 bushels among 100 people. The problem carries no
    instance data, so every number below is the puzzle statement.
    """
    del instance

    problem = pulp.LpProblem("abbots", pulp.LpMinimize)
    men = pulp.LpVariable("men", 0, 100, cat="Integer")
    women = pulp.LpVariable("women", 0, 100, cat="Integer")
    children = pulp.LpVariable("children", 0, 100, cat="Integer")

    problem += men + women + children == 100
    # Doubled through so the half-bushel child stays an integer.
    problem += 6 * men + 4 * women + children == 200
    problem += 5 * men == women

    return problem, {"men": men, "women": women, "children": children}
