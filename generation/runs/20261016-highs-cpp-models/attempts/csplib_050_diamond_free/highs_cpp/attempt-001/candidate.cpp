#include "dcp.h"

// Graph on N vertices, given by a symmetric 0/1 adjacency matrix with no loops.
// Output: the adjacency matrix. The constraints below describe the graph.
void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("N").get<int>();

  // the edge {u, v} is in the graph, one binary per unordered pair; the diagonal is 0 (no loop edges)
  std::vector<std::vector<dcp::Lin>> x(n, std::vector<dcp::Lin>(n, dcp::Lin(0)));
  for (int u = 0; u < n; ++u)
    for (int v = u + 1; v < n; ++v) {
      x[u][v] = dcp::new_var(h, 0, 1);
      x[v][u] = x[u][v];  // the graph is undirected: the matrix is symmetric
    }

  // the degree of each vertex is the number of edges incident on it
  std::vector<dcp::Lin> deg(n);
  for (int u = 0; u < n; ++u)
    for (int v = 0; v < n; ++v) deg[u] = deg[u] + x[u][v];

  // each degree is greater than zero and a multiple of 3: deg_u = 3 t_u with 1 <= t_u <= (n-1)/3
  int tmax = (n - 1) / 3;
  for (int u = 0; u < n; ++u) {
    dcp::Lin t = dcp::new_var(h, 1, tmax);
    dcp::add_row(h, deg[u] - 3.0 * t, 0, 0);
  }

  // the sum of the degrees is a multiple of 12: sum deg = 12 k
  dcp::Lin total;
  for (int u = 0; u < n; ++u) total = total + deg[u];
  dcp::Lin k = dcp::new_var(h, 0, n * (n - 1) / 12);
  dcp::add_row(h, total - 12.0 * k, 0, 0);

  // the degree sequence is in non-increasing order: deg_u >= deg_{u+1}
  for (int u = 0; u + 1 < n; ++u) dcp::add_row(h, deg[u] - deg[u + 1], 0, kHighsInf);

  // diamond-free: every set of four vertices has at most four edges between them
  for (int a = 0; a < n; ++a)
    for (int b = a + 1; b < n; ++b)
      for (int c = b + 1; c < n; ++c)
        for (int d = c + 1; d < n; ++d) {
          int quad[4] = {a, b, c, d};
          dcp::Lin edges;
          for (int i = 0; i < 4; ++i)
            for (int j = i + 1; j < 4; ++j) edges = edges + x[quad[i]][quad[j]];
          dcp::add_row(h, edges, -kHighsInf, 4);
        }

  out.add("matrix", x);
}
