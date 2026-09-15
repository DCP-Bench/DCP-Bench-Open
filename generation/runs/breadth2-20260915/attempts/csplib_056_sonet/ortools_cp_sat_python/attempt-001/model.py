from ortools.sat.python import cp_model


def build(instance):
    rings, nodes = instance["r"], instance["n"]
    demand, capacity = instance["demand"], instance["capacity_nodes"]
    model = cp_model.CpModel()
    on_ring = [[model.new_bool_var(f"ring_{k}_{i}") for i in range(nodes)] for k in range(rings)]
    for i in range(nodes):
        for j in range(i + 1, nodes):
            if demand[i][j] <= 0:
                continue
            together = []
            for k in range(rings):
                both = model.new_bool_var(f"both_{i}_{j}_{k}")
                model.add_bool_and(on_ring[k][i], on_ring[k][j]).only_enforce_if(both)
                model.add_bool_or(~on_ring[k][i], ~on_ring[k][j]).only_enforce_if(~both)
                together.append(both)
            model.add_bool_or(together)
    for k in range(rings):
        model.add(sum(on_ring[k]) <= capacity[k])
    adms = sum(on_ring[k][i] for k in range(rings) for i in range(nodes))
    model.minimize(adms)
    return model, {"ring_config": on_ring, "total_adms": adms}
