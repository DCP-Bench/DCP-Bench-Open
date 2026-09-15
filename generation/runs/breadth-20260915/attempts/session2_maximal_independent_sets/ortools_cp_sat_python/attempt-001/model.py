from ortools.sat.python import cp_model


def build(instance):
    adjacency = instance["adjacency_list"]
    n = len(adjacency)
    model = cp_model.CpModel()
    nodes = [model.new_bool_var(f"n_{i}") for i in range(n)]
    for i, neighbours in enumerate(adjacency):
        for neighbour in neighbours:
            j = neighbour - 1
            if i < j:
                model.add_at_most_one([nodes[i], nodes[j]])
        model.add_bool_or([nodes[i]] + [nodes[k - 1] for k in neighbours])
    return model, {"nodes": nodes}
