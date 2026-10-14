#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Graceful graphs: label the n nodes of a graph that has m edges with distinct
// labels from 0 to m so that, when every edge is labelled with the absolute
// difference of its two node labels, the edge labels are all different.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int m = instance.at("m").get<int>();  // number of edges
  const int n = instance.at("n").get<int>();  // number of nodes
  // graph[e] = [first node, second node] of edge e.
  const std::vector<std::vector<int>> graph =
      instance.at("graph").get<std::vector<std::vector<int>>>();

  // nodes[v] is the label of node v, from 0 to m; edges[e] is the label of
  // edge e, from 1 to m.
  std::vector<IntVar> nodes, edges;
  for (int v = 0; v < n; ++v) nodes.push_back(model.NewIntVar(Domain(0, m)));
  for (int e = 0; e < m; ++e) edges.push_back(model.NewIntVar(Domain(1, m)));

  // An edge's label is the absolute difference of the labels of its two nodes.
  for (int e = 0; e < m; ++e) {
    model.AddAbsEquality(edges[e], nodes[graph[e][0]] - nodes[graph[e][1]]);
  }

  // All edge labels are different, and all node labels are different.
  model.AddAllDifferent(edges);
  model.AddAllDifferent(nodes);

  json nodes_out = json::array();
  for (const IntVar& v : nodes) nodes_out.push_back(v.index());
  json edges_out = json::array();
  for (const IntVar& e : edges) edges_out.push_back(e.index());
  outputs = {{"nodes", nodes_out}, {"edges", edges_out}};
}
