# Maximum clique in a simple undirected graph G = (V, E) with n vertices.
# Output c[i] is 1 if vertex i is in the clique, 0 otherwise. Maximise the clique size.
import mip


def build(instance):
    n = instance["n"]
    adj = instance["adj"]

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")
    c = [model.add_var(f"c_{i}", var_type=mip.BINARY) for i in range(n)]

    # Every two distinct vertices in the clique must be adjacent: two vertices
    # that are not connected by an edge cannot both be selected.
    # A pair (i, j) with no edge in the graph cannot both be in the clique.
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i][j] == 0 or adj[j][i] == 0:
                model.add_constr(c[i] + c[j] <= 1)

    # The clique size is the objective to maximise.
    model.objective = mip.xsum(c)

    return model, {"c": c}
