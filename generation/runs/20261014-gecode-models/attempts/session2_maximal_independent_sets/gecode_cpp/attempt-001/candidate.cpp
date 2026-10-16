#include "dcp.h"

// Maximal independent set: choose a set of nodes of a graph such that no two
// chosen nodes are adjacent, and every node outside the set is adjacent to a
// chosen node. Output nodes[i] = 1 when node i is in the set.
class MaximalIndependentSet : public dcp::Space {
 protected:
  BoolVarArray in_set;  // in_set[i]: node i is in the independent set

 public:
  explicit MaximalIndependentSet(const json& instance) {
    int n = instance.at("n").get<int>();
    // adjacency_list[i] lists the neighbours of node i (1-based node ids)
    std::vector<std::vector<int>> adj = instance.at("adjacency_list").get<std::vector<std::vector<int>>>();

    in_set = BoolVarArray(*this, n, 0, 1);

    // symmetric neighbour sets, 0-based, so an edge listed on one side only still counts
    std::vector<std::vector<int>> nbr(n);
    for (int i = 0; i < n; ++i)
      for (int j : adj[i]) {
        int k = j - 1;
        if (k == i) continue;
        nbr[i].push_back(k);
        nbr[k].push_back(i);
      }
    for (int i = 0; i < n; ++i) {
      std::sort(nbr[i].begin(), nbr[i].end());
      nbr[i].erase(std::unique(nbr[i].begin(), nbr[i].end()), nbr[i].end());
    }

    // no two adjacent nodes are both in the set: each edge {i, j} has at most one chosen end
    for (int i = 0; i < n; ++i)
      for (int j : nbr[i]) {
        if (j <= i) continue;
        BoolVarArgs edge;
        edge << in_set[i] << in_set[j];
        linear(*this, edge, IRT_LQ, 1);
      }

    // the set is maximal: each node is in the set or has a neighbour in the set
    for (int i = 0; i < n; ++i) {
      BoolVarArgs cover;
      cover << in_set[i];
      for (int j : nbr[i]) cover << in_set[j];
      clause(*this, BOT_OR, cover, BoolVarArgs(), 1);
    }

    branch(*this, in_set, BOOL_VAR_NONE(), BOOL_VAL_MIN());
    output("nodes", in_set);
  }

  MaximalIndependentSet(MaximalIndependentSet& s) : dcp::Space(s) {
    in_set.update(*this, s.in_set);
  }
  Gecode::Space* copy() override { return new MaximalIndependentSet(*this); }
};

DCP_MODEL(MaximalIndependentSet)
