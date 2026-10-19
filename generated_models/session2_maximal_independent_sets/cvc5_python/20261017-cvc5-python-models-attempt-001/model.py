# Maximal independent set on a graph given by adjacency lists (1-based node ids).
# Output nodes[i] is True when node i+1 is in the maximal independent set.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    adj = instance["adjacency_list"]
    nodes = [cz.Bool(f"node_{i}") for i in range(n)]

    constraints = []

    # no two of which are adjacent: an independent set
    for i in range(n):
        for j in adj[i]:
            constraints.append(cz.Not(cz.And(nodes[i], nodes[j - 1])))

    # a maximal independent set: a node outside the set has a neighbour inside it,
    # so the set is not a subset of any other independent set
    for i in range(n):
        neighbours = [nodes[j - 1] for j in adj[i]]
        if neighbours:
            cover = neighbours[0] if len(neighbours) == 1 else cz.Or(neighbours)
            constraints.append(cz.Or(nodes[i], cover))
        else:
            constraints.append(nodes[i])

    return constraints, {"nodes": nodes}
