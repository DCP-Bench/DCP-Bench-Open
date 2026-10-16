#include "dcp.h"

// Maximum clique: given an undirected graph on n vertices, choose a set of
// vertices that are pairwise adjacent, of largest possible size. Output c[i] = 1
// when vertex i is in the clique.
class MaxClique : public dcp::Space {
 protected:
  BoolVarArray c;   // c[i]: vertex i is in the clique
  IntVar size;      // number of vertices in the clique

 public:
  explicit MaxClique(const json& instance) {
    int n = instance.at("n").get<int>();
    const auto& adj = instance.at("adj");

    c = BoolVarArray(*this, n, 0, 1);

    // two distinct vertices that are not adjacent cannot both be in the clique
    for (int i = 0; i < n; ++i)
      for (int j = i + 1; j < n; ++j)
        if (adj[i][j].get<int>() == 0) {
          BoolVarArgs pair;
          pair << c[i] << c[j];
          linear(*this, pair, IRT_LQ, 1);
        }

    // the clique size is the number of chosen vertices
    size = expr(*this, sum(c));

    // branch on vertices with the most neighbours first, and try including them first
    std::vector<int> degree(n, 0);
    for (int i = 0; i < n; ++i)
      for (int j = 0; j < n; ++j)
        if (j != i && adj[i][j].get<int>() == 1) ++degree[i];
    std::vector<int> order(n);
    for (int i = 0; i < n; ++i) order[i] = i;
    std::stable_sort(order.begin(), order.end(),
                     [&](int a, int b) { return degree[a] > degree[b]; });
    BoolVarArgs by_degree(n);
    for (int k = 0; k < n; ++k) by_degree[k] = c[order[k]];
    branch(*this, by_degree, BOOL_VAR_NONE(), BOOL_VAL_MAX());

    // the clique we want is as large as possible
    maximize(size);
    output("c", c);
  }

  MaxClique(MaxClique& s) : dcp::Space(s) {
    c.update(*this, s.c);
    size.update(*this, s.size);
  }
  Gecode::Space* copy() override { return new MaxClique(*this); }
};

DCP_MODEL(MaxClique)
