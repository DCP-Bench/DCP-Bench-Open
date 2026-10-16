// Graceful graphs: label the nodes of a graph with q edges by distinct integers from 0 to q,
// so that the absolute differences of the labels across the edges are all different.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int m = instance.at("m");
  int n = instance.at("n");
  json graph = instance.at("graph");

  // label[v] = label of node v, one of 0..m
  vec<IntVar*> label;
  createVars(label, n, 0, m);

  // every node has its own label
  all_different(label);

  // edge labels: the absolute difference of the labels of the two end nodes of each edge
  vec<IntVar*> edge;
  for (int k = 0; k < m; ++k) {
    int u = graph[k][0];
    int v = graph[k][1];
    IntVar* diff = newIntVar(-m, m);
    int_minus(label[u], label[v], diff);
    IntVar* len = newIntVar(1, m);
    int_abs(diff, len);
    edge.push(len);
  }

  // all edge labels are different
  all_different(edge);

  // search over the node labels first, then the edge labels
  branch(label, VAR_INORDER, VAL_MIN);
  branch(edge, VAR_INORDER, VAL_MIN);

  json nodes = json::array();
  for (int v = 0; v < n; ++v) nodes.push_back(dcp::out(label[v]));
  json edges = json::array();
  for (int k = 0; k < m; ++k) edges.push_back(dcp::out(edge[k]));
  outputs = {{"nodes", nodes}, {"edges", edges}};
}
