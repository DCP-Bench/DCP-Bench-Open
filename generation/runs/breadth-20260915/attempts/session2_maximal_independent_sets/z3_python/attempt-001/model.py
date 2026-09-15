import z3


def build(instance):
    adjacency = instance["adjacency_list"]
    n = len(adjacency)
    nodes = [z3.Bool(f"n_{i}") for i in range(n)]
    constraints = []
    for i, neighbours in enumerate(adjacency):
        for neighbour in neighbours:
            j = neighbour - 1
            if i < j:
                constraints.append(z3.Not(z3.And(nodes[i], nodes[j])))
        constraints.append(z3.Or([nodes[i]] + [nodes[k - 1] for k in neighbours]))
    return constraints, {"nodes": nodes}
