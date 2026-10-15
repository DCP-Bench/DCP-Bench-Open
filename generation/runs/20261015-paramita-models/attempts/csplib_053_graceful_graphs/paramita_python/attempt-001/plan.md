A labelling f of the nodes of a graph with q edges is graceful if f assigns each node a unique label from {0, 1, ..., q} -> f[v][l] one-hot over labels 0..m, exactly one per node (sum_l f[v][l] == 1)
each node a unique label -> per label l, sum_v f[v][l] <= 1
when each edge xy is labelled with |f(x) - f(y)| -> per edge e and label pair (lx, ly), lx != ly: If(f[x][lx] & f[y][ly], d[e][|lx-ly|]); d[e][k] one-hot over k in 1..m (sum_k d[e][k] == 1)
the edge labels are all different -> per k in 1..m, sum_e d[e][k] == 1 (edge labels form a permutation of 1..m)
Print the node labels and edge labels (nodes, edges) -> outputs nodes = sum_l l*f[v][l], edges = sum_k k*d[e][k]
objective: satisfaction (no objective)
