A labelling f of the nodes of a graph with q edges is graceful if f assigns each node a unique label from {0..q} -> node labels: IntVar[n] in 0..q, allDifferent(nodes, "AC")
and when each edge xy is labelled with |f(x)-f(y)|, the edge labels are all different -> edge[e] = |nodes[x] - nodes[y]| via .sub().abs().intVar(); allDifferent(edges, "AC")
Print the node labels and edge labels (nodes, edges) -> out.put("nodes", nodes); out.put("edges", edges)
Objective: none (satisfaction)
