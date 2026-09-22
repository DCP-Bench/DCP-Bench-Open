# Largest set of mutually adjacent vertices.
from hermax.model import Model


def build(instance):
    n = instance["n"]
    adj = instance["adj"]

    m = Model()
    chosen = m.bool_vector("chosen", n)
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i][j] == 0:
                m &= (~chosen[i] | ~chosen[j])

    # Maximising the clique: every vertex left out costs one.
    for i in range(n):
        m.obj[1] += chosen[i]
    return m, {"c": chosen}
