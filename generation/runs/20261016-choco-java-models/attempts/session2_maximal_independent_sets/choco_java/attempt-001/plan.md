Problem: a maximal independent set of an undirected graph given as adjacency lists (1-based, symmetric).
Output nodes[i] = 1 if node i is in the set.

- "no two of which are adjacent" -> for each node i and each neighbour j: x_i + x_j <= 1 -> m.sum({x_i, x_j}, "<=", 1)
- "not a subset of any other independent set" (maximal) -> for each node i: x_i or some neighbour of i is in the set -> m.sum({x_i} + neighbours of i, ">=", 1)
- "find a maximal independent set" (satisfaction, no objective) -> default search over the node booleans
