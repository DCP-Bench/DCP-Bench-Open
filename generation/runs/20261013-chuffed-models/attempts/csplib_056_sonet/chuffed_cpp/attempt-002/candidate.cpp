// SONET network design: place nodes on SONET rings so that every pair of nodes with traffic shares a ring, ring capacities are respected, and the number of add-drop multiplexers (one per node per ring) is minimal.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");                              // number of nodes
  int r = instance.at("r");                              // number of rings
  std::vector<int> cap = instance.at("capacity_nodes").get<std::vector<int>>();  // nodes each ring can host
  const json& demand = instance.at("demand");            // demand[i][j]: traffic between nodes i and j

  // on[k][i] = 1 if node i is installed on ring k (one add-drop multiplexer)
  vec<vec<BoolView>> on;
  createVars(on, r, n);
  // the same as integers, for export and for counting the multiplexers
  vec<vec<IntVar*>> on_int;
  for (int k = 0; k < r; ++k) {
    on_int.push();
    for (int i = 0; i < n; ++i) {
      IntVar* v = newIntVar(0, 1);
      bool2int(on[k][i], v);
      on_int.last().push(v);
    }
  }

  // a ring hosts at most its capacity of nodes
  for (int k = 0; k < r; ++k) {
    // ring k can host at most cap[k] nodes
    bool_linear(on[k], IRT_LE, getConstant(cap[k]));
  }

  // two nodes with traffic between them must be on a common ring
  for (int i = 0; i < n; ++i) {
    for (int j = i + 1; j < n; ++j) {
      if (demand[i][j].get<int>() + demand[j][i].get<int>() == 0) continue;
      // both[k] = 1 if nodes i and j are both on ring k
      vec<BoolView> common;
      for (int k = 0; k < r; ++k) {
        BoolView both = newBoolVar();
        vec<BoolView> pair;
        pair.push(on[k][i]);
        pair.push(on[k][j]);
        array_bool_and(pair, both);
        common.push(both);
      }
      bool_clause(common);
    }
  }

  // total is the number of add-drop multiplexers used, i.e. the nodes installed on all rings
  int max_adm = r * n;
  IntVar* total = newIntVar(0, max_adm);
  vec<IntVar*> all;
  vec<int> ones;
  for (int k = 0; k < r; ++k) {
    for (int i = 0; i < n; ++i) {
      all.push(on_int[k][i]);
      ones.push(1);
    }
  }
  int_linear(ones, all, IRT_EQ, total);

  // branch on ring membership ring by ring, leaving nodes off rings first
  branch(all, VAR_INORDER, VAL_MIN);
  optimize(total, OPT_MIN);

  json config = json::array();
  for (int k = 0; k < r; ++k) {
    json row = json::array();
    for (int i = 0; i < n; ++i) row.push_back(dcp::out(on_int[k][i]));
    config.push_back(row);
  }
  outputs = {{"ring_config", config}, {"total_adms", dcp::out(total)}};
}
