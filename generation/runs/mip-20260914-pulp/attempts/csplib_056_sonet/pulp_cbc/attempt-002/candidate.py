import pulp


def build(instance):
    rings, nodes = range(instance["r"]), range(instance["n"])
    demand, capacity = instance["demand"], instance["capacity_nodes"]
    problem = pulp.LpProblem("sonet", pulp.LpMinimize)
    on_ring = [[pulp.LpVariable(f"ring_{k}_{i}", cat="Binary") for i in nodes] for k in rings]
    for i in nodes:
        for j in nodes:
            if j <= i or demand[i][j] <= 0:
                continue
            # together[k] == on_ring[k][i] and on_ring[k][j]
            together = []
            for k in rings:
                both = pulp.LpVariable(f"both_{i}_{j}_{k}", cat="Binary")
                problem += both <= on_ring[k][i]
                problem += both <= on_ring[k][j]
                problem += both >= on_ring[k][i] + on_ring[k][j] - 1
                together.append(both)
            problem += pulp.lpSum(together) >= 1
    for k in rings:
        problem += pulp.lpSum(on_ring[k]) <= capacity[k]
    adms = pulp.lpSum(on_ring[k][i] for k in rings for i in nodes)
    problem += adms
    return problem, {"ring_config": on_ring, "total_adms": adms}
