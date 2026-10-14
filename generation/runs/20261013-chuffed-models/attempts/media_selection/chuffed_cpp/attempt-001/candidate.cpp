// Media selection: choose advertising media so that every target audience is reached by at least one selected medium, at minimum total cost.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> costs = instance.at("media_costs").get<std::vector<int>>();
  std::vector<std::vector<int>> reach = instance.at("incidence_matrix").get<std::vector<std::vector<int>>>();  // reach[a][m] = 1 if medium m reaches audience a
  int nm = static_cast<int>(costs.size());   // number of media
  int na = static_cast<int>(reach.size());   // number of audiences

  // sel[m] = 1 if medium m is selected; the Boolean is exported through the 0..1 integer is_sel[m]
  vec<BoolView> sel;
  createVars(sel, nm);
  vec<IntVar*> is_sel;
  for (int m = 0; m < nm; ++m) {
    IntVar* v = newIntVar(0, 1);
    bool2int(sel[m], v);
    is_sel.push(v);
  }

  // every audience must be covered: at least one selected medium reaches it
  for (int a = 0; a < na; ++a) {
    // the media that reach audience a
    vec<BoolView> covering;
    for (int m = 0; m < nm; ++m) {
      if (reach[a][m] == 1) covering.push(sel[m]);
    }
    bool_clause(covering);
  }

  // total is the cost of the selected media
  int max_cost = 0;
  vec<int> coef;
  for (int m = 0; m < nm; ++m) {
    coef.push(costs[m]);
    max_cost += costs[m];
  }
  IntVar* total = newIntVar(0, max_cost);
  int_linear(coef, is_sel, IRT_EQ, total);

  // branch on the selection decisions, medium by medium
  branch(is_sel, VAR_INORDER, VAL_MIN);
  optimize(total, OPT_MIN);

  json selected = json::array();
  for (int m = 0; m < nm; ++m) selected.push_back(dcp::out(is_sel[m]));
  outputs = {{"is_selected", selected}, {"min_total_cost", dcp::out(total)}};
}
