Given a simple undirected graph \( G = (V, E) \), where \( V \) is the set of vertices and \( E \) the set of undirected edges,
the edge \(\{u, v\}\) is in \( E \) if and only if vertex \( u \) is adjacent to vertex \( v \in G \). The graph is simple in
that there are no loop edges, i.e., we have no edges of the form \(\{v, v\}\). Each vertex \( v \in V \) has a degree \( d_v \)
i.e., the number of edges incident on that vertex. Consequently, a graph has a degree sequence \( d_1, \ldots, d_n \), where
\( d_i \geq d_{i+1} \). A diamond is a set of four vertices in \( V \) such that there are at least five edges between those
vertices. Conversely, a graph is diamond-free if it has no diamond as an induced subgraph, i.e., for every set of four vertices
the number of edges between those vertices is at most four.

In our problem, we have additional properties required of the degree sequences of the graphs, in particular, that the degree
of each vertex is greater than zero (i.e., isolated vertices are disallowed), the degree of each vertex is divisible by 3, and the
sum of the degrees is divisible by 12 (i.e., \(|E|\) is divisible by 6).

The problem is then, for a given number of vertices, to find a simple diamond-free graph such that

- Each degree \( d_i > 0 \) and \( d_i \) is divisible by 3
- The sum of the degrees is divisible by 12

Print the adjacency matrix of the graph (matrix) as a list of lists of booleans.
