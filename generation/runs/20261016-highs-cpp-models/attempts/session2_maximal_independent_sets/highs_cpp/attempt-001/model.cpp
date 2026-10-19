// Maximal independent set: find a maximal independent set of a graph given by an adjacency
// list (1-based node numbers). Output nodes[i] is true when node i+1 is in the set.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int n = instance.at("n").get<int>();
  const json& adjacency = instance.at("adjacency_list");

  // one binary per node: 1 when the node is in the set
  std::vector<dcp::Lin> x;
  for (int i = 0; i < n; ++i) x.push_back(dcp::new_var(h, 0, 1));

  // no two of the nodes in the set are adjacent
  for (int i = 0; i < n; ++i) {
    for (const auto& j : adjacency.at(i)) {
      int k = j.get<int>() - 1;
      dcp::add_row(h, x[i] + x[k], -kHighsInf, 1);
    }
  }

  // every node outside the set has a neighbour in the set, so the set cannot be extended
  for (int i = 0; i < n; ++i) {
    dcp::Lin cover = x[i];
    for (const auto& j : adjacency.at(i)) {
      int k = j.get<int>() - 1;
      cover = cover + x[k];
    }
    dcp::add_row(h, cover, 1, kHighsInf);
  }

  out.add("nodes", x);
}
