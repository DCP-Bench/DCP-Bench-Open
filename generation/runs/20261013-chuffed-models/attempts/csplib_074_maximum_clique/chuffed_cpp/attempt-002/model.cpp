// Maximum clique: find the largest set of vertices of an undirected graph in which every
// two distinct vertices are adjacent.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");
  std::vector<std::vector<int>> adj = instance.at("adj").get<std::vector<std::vector<int>>>();

  // c[i] = 1 if vertex i is in the clique
  vec<IntVar*> c;
  createVars(c, n, 0, 1, true);

  // every two distinct vertices of the clique are adjacent:
  // two vertices that are not connected by an edge cannot both be chosen
  for (int i = 0; i < n; ++i)
    for (int j = i + 1; j < n; ++j)
      if (!adj[i][j]) bin_linear(c[i], c[j], IRT_LE, 1);

  // maximize the size of the clique
  IntVar* size = newIntVar(0, n);
  int_linear(c, IRT_EQ, size);

  branch(c, VAR_INORDER, VAL_MAX);
  optimize(size, OPT_MAX);

  json arr = json::array();
  for (int i = 0; i < n; ++i) arr.push_back(dcp::out(c[i]));
  outputs = {{"c", arr}};
}
