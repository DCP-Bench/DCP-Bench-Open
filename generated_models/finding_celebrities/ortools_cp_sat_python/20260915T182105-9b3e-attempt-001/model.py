from ortools.sat.python import cp_model


def build(instance):
    """Finding celebrities: everyone knows a celebrity, and a celebrity knows
    only other celebrities.
    """
    graph = instance["graph"]
    n = len(graph)

    model = cp_model.CpModel()
    celebrities = [model.new_bool_var(f"c{i}") for i in range(n)]
    num_celebrities = model.new_int_var(1, n, "num_celebrities")

    model.add(num_celebrities == sum(celebrities))

    for i in range(n):
        # Both halves read the fixed acquaintance graph, so the first is a
        # plain Python truth value and only the second needs reifying.
        known_by_everyone = sum(graph[j][i] for j in range(n)) == n
        knows_count = sum(graph[i][j] for j in range(n))
        if not known_by_everyone:
            model.add(celebrities[i] == 0)
            continue
        model.add(knows_count == num_celebrities).only_enforce_if(celebrities[i])
        model.add(knows_count != num_celebrities).only_enforce_if(~celebrities[i])

    return model, {"celebrities": celebrities}
