import cpmpy as cp


def build(instance):
    graph = instance["graph"]
    # The reference fixes the country count; it is the largest 1-based node id.
    nodes = max(max(edge) for edge in graph)
    colors = cp.intvar(1, nodes, shape=nodes, name="colors")
    model = cp.Model([colors[i - 1] != colors[j - 1] for i, j in graph])
    model.minimize(cp.max([colors[k] for k in range(nodes)]))
    return model, {"colors": [colors[k] for k in range(nodes)]}
