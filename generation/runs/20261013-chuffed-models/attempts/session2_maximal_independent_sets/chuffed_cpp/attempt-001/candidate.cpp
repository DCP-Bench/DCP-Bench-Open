// Maximal independent set: choose a set of graph nodes with no two adjacent nodes, to which no other
// node can be added without breaking that rule.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");
  std::vector<std::vector<int>> adj = instance.at("adjacency_list").get<std::vector<std::vector<int>>>();

  // inset[i] is true when node i+1 is in the independent set
  vec<BoolView> inset;
  createVars(inset, n);

  // no two adjacent nodes are both in the set (each edge is listed from both ends, so post it once)
  for (int i = 0; i < n; ++i) {
    for (int j : adj[i]) {
      if (j - 1 <= i) continue;
      BoolView not_i = ~inset[i];
      BoolView not_j = ~inset[j - 1];
      vec<BoolView> edge;
      edge.push(not_i);
      edge.push(not_j);
      bool_clause(edge);
    }
  }

  // maximality: every node is in the set or has a neighbour in the set
  for (int i = 0; i < n; ++i) {
    vec<BoolView> cover;
    cover.push(inset[i]);
    for (int j : adj[i]) cover.push(inset[j - 1]);
    bool_clause(cover);
  }

  // the nodes are the decision variables; export each membership flag as a 0/1 integer
  vec<IntVar*> flags;
  for (int i = 0; i < n; ++i) {
    IntVar* e = newIntVar(0, 1);
    bool2int(inset[i], e);
    flags.push(e);
  }
  branch(flags, VAR_INORDER, VAL_MIN);

  json arr = json::array();
  for (int i = 0; i < n; ++i) arr.push_back(dcp::out(flags[i]));
  outputs = {{"nodes", arr}};
}
