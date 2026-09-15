from ortools.sat.python import cp_model


def build(instance):
    graph = instance["graph"]
    # The reference fixes the country count; it is the largest 1-based node id.
    nodes = max(max(edge) for edge in graph)
    model = cp_model.CpModel()
    colors = [model.new_int_var(1, nodes, f"c_{k}") for k in range(nodes)]
    for i, j in graph:
        model.add(colors[i - 1] != colors[j - 1])
    used = model.new_int_var(1, nodes, "used")
    model.add_max_equality(used, colors)
    model.minimize(used)
    return model, {"colors": colors}
