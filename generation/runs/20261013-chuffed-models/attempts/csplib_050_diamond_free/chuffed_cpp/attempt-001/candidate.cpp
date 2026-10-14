// Diamond-free degree sequences: find a simple graph on N vertices with no diamond (no four vertices
// spanned by five or more edges), whose degrees are positive multiples of 3, sorted in non-increasing
// order, with a degree sum that is a multiple of 12. The output is its adjacency matrix.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("N");
  int max_k = (n - 1) / 3;  // a degree 3*k is at most n-1, so k is at most (n-1)/3

  // adj[i][j] = 1 if vertices i and j are adjacent; the matrix is symmetric and has no loops
  std::vector<std::vector<IntVar*>> adj(n, std::vector<IntVar*>(n, nullptr));
  vec<IntVar*> edges;
  for (int i = 0; i < n; ++i) {
    adj[i][i] = getConstant(0);  // a simple graph has no loop edges
    for (int j = i + 1; j < n; ++j) {
      IntVar* e;
      createVar(e, 0, 1, true);
      adj[i][j] = e;
      adj[j][i] = e;
      edges.push(e);
    }
  }

  // no diamond: for every four vertices, the number of edges among them is at most four
  for (int a = 0; a < n; ++a)
    for (int b = a + 1; b < n; ++b)
      for (int c = b + 1; c < n; ++c)
        for (int d = c + 1; d < n; ++d) {
          vec<IntVar*> six;
          six.push(adj[a][b]);
          six.push(adj[a][c]);
          six.push(adj[a][d]);
          six.push(adj[b][c]);
          six.push(adj[b][d]);
          six.push(adj[c][d]);
          int_linear(six, IRT_LE, 4);
        }

  // the degree of each vertex is a positive multiple of 3: degree_i = 3 * k[i] with k[i] >= 1
  vec<IntVar*> ks;
  for (int i = 0; i < n; ++i) {
    IntVar* k = newIntVar(1, max_k);
    ks.push(k);
    vec<int> coef;
    vec<IntVar*> vars;
    for (int j = 0; j < n; ++j) {
      if (j == i) continue;
      coef.push(1);
      vars.push(adj[i][j]);
    }
    coef.push(-3);
    vars.push(k);
    int_linear(coef, vars, IRT_EQ, 0);
  }

  // the degree sequence is sorted: d[i] >= d[i+1], which is k[i] >= k[i+1]
  for (int i = 0; i + 1 < n; ++i) int_rel(ks[i], IRT_GE, ks[i + 1], 0);

  // the sum of the degrees is 3 * (sum of k) and must be a multiple of 12, so sum of k is a multiple of 4
  IntVar* sum_k = newIntVar(n, n * max_k);
  int_linear(ks, IRT_EQ, sum_k);
  IntVar* quarters = newIntVar(0, n * max_k / 4);
  vec<int> q_coef;
  q_coef.push(1);
  q_coef.push(-4);
  vec<IntVar*> q_vars;
  q_vars.push(sum_k);
  q_vars.push(quarters);
  int_linear(q_coef, q_vars, IRT_EQ, 0);

  branch(edges, VAR_INORDER, VAL_MIN);

  json matrix = json::array();
  for (int i = 0; i < n; ++i) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(dcp::out(adj[i][j]));
    matrix.push_back(row);
  }
  outputs = {{"matrix", matrix}};
}
