import pulp


def build(instance):
    adjacency = instance["adjacency_list"]
    problem = pulp.LpProblem("maximal_independent_set", pulp.LpMinimize)
    nodes = [pulp.LpVariable(f"node_{i}", cat="Binary") for i in range(len(adjacency))]
    for i, neighbours in enumerate(adjacency):
        for neighbour in neighbours:
            j = neighbour - 1
            if i < j:
                problem += nodes[i] + nodes[j] <= 1
        # Maximality: selected, or next to something selected.
        problem += nodes[i] + pulp.lpSum(nodes[k - 1] for k in neighbours) >= 1
    return problem, {"nodes": nodes}
