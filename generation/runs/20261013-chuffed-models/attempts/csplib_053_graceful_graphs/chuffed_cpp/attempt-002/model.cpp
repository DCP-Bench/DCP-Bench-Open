// Graceful graphs: label the nodes of a graph with q edges by distinct numbers from
// 0..q so that the edge labels |f(x) - f(y)| are all different.
#include "dcp.h"

#include <vector>

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");  // number of nodes
  int m = instance.at("m");  // number of edges, q
  std::vector<std::vector<int>> graph = instance.at("graph").get<std::vector<std::vector<int>>>();

  // nodes[v] is the label of node v, a value in 0..q
  vec<IntVar*> nodes;
  createVars(nodes, n, 0, m);

  // each node gets a unique label
  all_different(nodes);

  // edges[k] is the label of edge k: the absolute difference of the labels of its two ends
  vec<IntVar*> edges;
  createVars(edges, m, 0, m);
  for (int k = 0; k < m; ++k) {
    int u = graph[k][0];
    int v = graph[k][1];
    // diff = f(u) - f(v), in -q..q
    IntVar* diff = newIntVar(-m, m);
    int_minus(nodes[u], nodes[v], diff);
    // edges[k] = |f(u) - f(v)|
    int_abs(diff, edges[k]);
  }

  // all edge labels are different
  all_different(edges);

  // branch on the node labels first, then the edge labels
  branch(nodes, VAR_INORDER, VAL_MIN);
  branch(edges, VAR_INORDER, VAL_MIN);

  json node_arr = json::array();
  for (int i = 0; i < n; ++i) node_arr.push_back(dcp::out(nodes[i]));
  json edge_arr = json::array();
  for (int k = 0; k < m; ++k) edge_arr.push_back(dcp::out(edges[k]));
  outputs = {{"nodes", node_arr}, {"edges", edge_arr}};
}
