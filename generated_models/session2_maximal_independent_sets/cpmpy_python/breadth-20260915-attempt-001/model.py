import cpmpy as cp


def build(instance):
    adjacency = instance["adjacency_list"]
    n = len(adjacency)
    nodes = cp.boolvar(shape=n, name="nodes")
    model = cp.Model()
    for i, neighbours in enumerate(adjacency):
        for neighbour in neighbours:
            j = neighbour - 1
            if i < j:
                model += nodes[i] + nodes[j] <= 1
        # Maximality: selected, or next to something selected.
        model += cp.any([nodes[i]] + [nodes[k - 1] for k in neighbours])
    return model, {"nodes": [nodes[i] for i in range(n)]}
