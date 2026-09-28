"""Maximum clique: choose as many vertices as possible such that every two of them are adjacent."""
from docplex.mp.model import Model


def build(instance):
    n, adj = instance["n"], instance["adj"]

    model = Model("maximum_clique")

    # c[i] is 1 when vertex i is in the clique.
    c = model.binary_var_list(n, name="c")

    # Two vertices that are not connected cannot both be in the clique. One
    # constraint per vertex covers all its later non-neighbours at once: when i
    # is in the clique, none of them is. The pairwise form needs one constraint
    # per non-edge, 1312 on the largest instance, past the 1000 the Community
    # Edition allows; both forms admit exactly the same cliques.
    for i in range(n):
        later = [j for j in range(i + 1, n) if adj[i][j] == 0]
        if later:
            model.add_constraint(model.sum(c[j] for j in later) <= len(later) * (1 - c[i]),
                                 ctname=f"non_neighbours_{i}")

    # Maximise the size of the clique.
    model.maximize(model.sum(c))

    return model, {"c": c}
