#include "dcp.h"

// SONET ring configuration: install the nodes on rings so that every pair of
// nodes with traffic between them shares at least one ring, each ring holds at
// most its capacity of nodes, and the total number of add-drop multiplexers
// (one per node installed on a ring) is minimal.
class SonetRings : public dcp::Space {
 protected:
  int r_, n_;
  BoolVarArray on;  // on[k*n + i]: node i is on ring k (ring_config[k][i])
  IntVar adms;      // total number of ADMs

 public:
  explicit SonetRings(const json& instance) {
    int n = instance.at("n").get<int>();
    int r = instance.at("r").get<int>();
    std::vector<int> capacity = instance.at("capacity_nodes");
    const json& demand = instance.at("demand");
    n_ = n;
    r_ = r;

    // node i is on ring k or not
    on = BoolVarArray(*this, r * n, 0, 1);

    // a ring hosts at most its capacity of nodes
    for (int k = 0; k < r; ++k) {
      BoolVarArgs ring;
      for (int i = 0; i < n; ++i) ring << on[k * n + i];
      linear(*this, ring, IRT_LQ, capacity[k]);
    }

    // two nodes that exchange traffic must share a ring: for each pair, at
    // least one ring holds both. No global fits this (it is a per-ring
    // conjunction), so each ring gives a Boolean "both on this ring".
    for (int i = 0; i < n; ++i) {
      for (int j = i + 1; j < n; ++j) {
        if (demand[i][j].get<int>() == 0 && demand[j][i].get<int>() == 0) continue;
        BoolVarArgs shared;
        for (int k = 0; k < r; ++k) shared << expr(*this, on[k * n + i] && on[k * n + j]);
        linear(*this, shared, IRT_GQ, 1);
      }
    }

    // the total number of ADMs is the number of (node, ring) installations
    BoolVarArgs all;
    for (int k = 0; k < r; ++k)
      for (int i = 0; i < n; ++i) all << on[k * n + i];
    adms = expr(*this, sum(all));
    minimize(adms);

    branch(*this, on, BOOL_VAR_DEGREE_MAX(), BOOL_VAL_MIN());

    std::vector<BoolVarArgs> ring_config;
    for (int k = 0; k < r; ++k) {
      BoolVarArgs row;
      for (int i = 0; i < n; ++i) row << on[k * n + i];
      ring_config.push_back(row);
    }
    output("ring_config", ring_config);
    output("total_adms", adms);
  }

  SonetRings(SonetRings& s) : dcp::Space(s), r_(s.r_), n_(s.n_) {
    on.update(*this, s.on);
    adms.update(*this, s.adms);
  }
  Gecode::Space* copy() override { return new SonetRings(*this); }
};

DCP_MODEL(SonetRings)
