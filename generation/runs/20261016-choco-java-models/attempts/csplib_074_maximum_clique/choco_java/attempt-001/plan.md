Given a simple undirected graph G = (V, E), find a clique (a subset of vertices where every two distinct vertices are adjacent) of largest size.
  -> BoolVar x[i] per vertex (x[i] = 1 if vertex i is in the clique)
Print c[i] = 1 if vertex i is in the maximum clique, 0 otherwise.
  -> output c = x
every two distinct vertices in the subset are adjacent (for each non-adjacent pair i < j, not both in the clique)
  -> x[i] + x[j] <= 1 (m.arithm(x[i], "+", x[j], "<=", 1) or sum of two BoolVars), no global fits
adjacency comes from the instance field adj (n x n 0/1 matrix)
  -> only non-adjacent pairs of the instance are posted
maximum clique size: maximize the number of chosen vertices
  -> objective: size = sum(x), MAXIMIZE
