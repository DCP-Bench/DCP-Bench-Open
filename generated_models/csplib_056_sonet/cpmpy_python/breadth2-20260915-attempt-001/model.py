import cpmpy as cp


def build(instance):
    rings, nodes = instance["r"], instance["n"]
    demand, capacity = instance["demand"], instance["capacity_nodes"]
    on_ring = cp.boolvar(shape=(rings, nodes), name="ring_config")
    model = cp.Model()
    for i in range(nodes):
        for j in range(i + 1, nodes):
            if demand[i][j] > 0:
                # The pair must share a ring.
                model += cp.any([on_ring[k, i] & on_ring[k, j] for k in range(rings)])
    for k in range(rings):
        model += cp.sum([on_ring[k, i] for i in range(nodes)]) <= capacity[k]
    adms = cp.sum([on_ring[k, i] for k in range(rings) for i in range(nodes)])
    model.minimize(adms)
    return model, {"ring_config": [[on_ring[k, i] for i in range(nodes)] for k in range(rings)],
                   "total_adms": adms}
