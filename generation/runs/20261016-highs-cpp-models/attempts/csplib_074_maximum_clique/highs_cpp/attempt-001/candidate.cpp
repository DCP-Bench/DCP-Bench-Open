// Problem csplib_074_maximum_clique: maximum clique in a simple undirected graph.
// Output c[i] is 1 if vertex i is in the clique, 0 otherwise; maximise the number of chosen vertices.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n").get<int>();
  const auto& adj = instance.at("adj");

  // vertex i is in the clique (binary column per vertex)
  std::vector<dcp::Lin> c;
  for (int i = 0; i < n; i++) {
    c.push_back(dcp::new_var(h, 0, 1));
  }

  // two distinct vertices that are not adjacent cannot both be in the clique
  for (int i = 0; i < n; i++) {
    for (int j = i + 1; j < n; j++) {
      bool adjacent = adj[i][j].get<int>() != 0 && adj[j][i].get<int>() != 0;
      if (!adjacent) {
        // c_i + c_j <= 1
        dcp::add_row(h, c[i] + c[j], -kHighsInf, 1);
      }
    }
  }

  // maximise the number of vertices in the clique
  dcp::Lin size = 0;
  for (int i = 0; i < n; i++) {
    size = size + c[i];
  }
  out.maximize(size);

  // the declared output c, one binary per vertex
  out.add("c", c);
}
