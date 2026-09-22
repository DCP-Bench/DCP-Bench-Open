# An independent set that no unchosen node could be added to.
from hermax.model import Model


def build(instance):
    n = instance["n"]
    adjacency = instance["adjacency_list"]

    m = Model()
    nodes = m.bool_vector("nodes", n)
    for i, neighbours in enumerate(adjacency):
        for neighbour in neighbours:
            j = neighbour - 1
            if i < j:
                m &= (~nodes[i] | ~nodes[j])
        # Maximal: a node left out must have a chosen neighbour blocking it.
        clause = nodes[i]
        for k in neighbours:
            clause = clause | nodes[k - 1]
        m &= clause
    return m, {"nodes": nodes}
