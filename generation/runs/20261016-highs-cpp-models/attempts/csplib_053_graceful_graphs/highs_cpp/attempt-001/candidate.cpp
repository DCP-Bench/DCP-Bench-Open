// Graceful graphs (CSPLib 053). A graph has n nodes and m edges. A labelling f of the
// nodes assigns each node a unique label from {0, 1, ..., m}, and when each edge xy is
// labelled with |f(x) - f(y)|, the edge labels are all different. Print the node labels
// and edge labels (nodes, edges).
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int n = instance.at("n").get<int>();
  const int m = instance.at("m").get<int>();
  const auto& graph = instance.at("graph");
  // Labels lie in 0..m, so two labels differ by at most m and an edge label is at most m.
  // The sum of a label difference (at most m in size) and an edge label (at most m) is at
  // most 2m in size, which bounds the big-M constant.
  const double M = 2.0 * m;

  // y[i][v] = 1 when node i has label v. The node label f[i] is the value picked by y.
  std::vector<std::vector<dcp::Lin>> y(n, std::vector<dcp::Lin>(m + 1));
  std::vector<dcp::Lin> f(n);
  for (int i = 0; i < n; ++i) {
    // each node takes exactly one label from 0..m
    dcp::Lin one_label;
    for (int v = 0; v <= m; ++v) {
      y[i][v] = dcp::new_var(h, 0, 1);
      one_label = one_label + y[i][v];
      f[i] = f[i] + static_cast<double>(v) * y[i][v];
    }
    dcp::add_row(h, one_label, 1, 1);
  }
  // every label is used by at most one node, so the node labels are unique
  for (int v = 0; v <= m; ++v) {
    dcp::Lin users;
    for (int i = 0; i < n; ++i) users = users + y[i][v];
    dcp::add_row(h, users, -kHighsInf, 1);
  }

  // z[e][k] = 1 when edge e has label k, for k in 1..m. The edge label d[e] is the value picked by z.
  std::vector<std::vector<dcp::Lin>> z(m, std::vector<dcp::Lin>(m + 1));
  std::vector<dcp::Lin> d(m);
  for (int e = 0; e < m; ++e) {
    const int a = graph[e][0].get<int>();
    const int b = graph[e][1].get<int>();
    // each edge takes exactly one label from 1..m
    dcp::Lin one_label;
    for (int k = 1; k <= m; ++k) {
      z[e][k] = dcp::new_var(h, 0, 1);
      one_label = one_label + z[e][k];
      d[e] = d[e] + static_cast<double>(k) * z[e][k];
    }
    dcp::add_row(h, one_label, 1, 1);

    // the edge label equals |f(a) - f(b)|: d >= f(a) - f(b) and d >= f(b) - f(a)
    dcp::add_row(h, d[e] - f[a] + f[b], 0, kHighsInf);
    dcp::add_row(h, d[e] + f[a] - f[b], 0, kHighsInf);
    // and d is at most the difference in the direction s chooses:
    // s = 1 gives d <= f(a) - f(b), s = 0 gives d <= f(b) - f(a)
    dcp::Lin s = dcp::new_var(h, 0, 1);
    dcp::add_row(h, d[e] - f[a] + f[b] + M * s, -kHighsInf, M);
    dcp::add_row(h, d[e] - f[b] + f[a] - M * s, -kHighsInf, 0);
  }
  // all edge labels are different: each label k is used by at most one edge
  for (int k = 1; k <= m; ++k) {
    dcp::Lin users;
    for (int e = 0; e < m; ++e) users = users + z[e][k];
    dcp::add_row(h, users, -kHighsInf, 1);
  }

  out.add("nodes", f);
  out.add("edges", d);
}
