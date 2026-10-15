Problem: find a maximal independent set of the graph given by adjacency_list (1-based, n nodes); output nodes[i] = 1 if node i is in the set.
- "no two of which are adjacent" -> for every edge (i, j): not (x_i and x_j)  -> ~(x_i & x_j)
- "not a subset of any other independent set" (maximal) -> every node not in the set has a neighbour in the set: x_i or OR of x_j over neighbours j  -> Or([x_i] + [x_j for j in N(i)])
- objective: none (satisfaction); output nodes = the x_i in node order
