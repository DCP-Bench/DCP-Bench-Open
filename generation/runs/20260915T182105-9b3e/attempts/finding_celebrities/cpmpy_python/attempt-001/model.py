import cpmpy as cp


def build(instance):
    """Finding celebrities: everyone knows a celebrity, and a celebrity knows
    only other celebrities.
    """
    graph = instance["graph"]
    n = len(graph)

    celebrities = cp.boolvar(shape=n, name="celebrities")
    num_celebrities = cp.intvar(1, n, name="num_celebrities")

    model = cp.Model(num_celebrities == cp.sum(celebrities))

    for i in range(n):
        # Both halves read the fixed acquaintance graph: how many people know
        # person i, and how many people person i knows.
        known_by_everyone = sum(graph[j][i] for j in range(n)) == n
        knows_count = sum(graph[i][j] for j in range(n))
        model += celebrities[i] == (
            cp.BoolVal(known_by_everyone) & (knows_count == num_celebrities)
        )

    return model, {"celebrities": celebrities}
