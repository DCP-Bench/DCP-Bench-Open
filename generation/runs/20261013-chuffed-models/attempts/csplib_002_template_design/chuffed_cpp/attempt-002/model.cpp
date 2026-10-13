// Template design: decide how many copies of each variation go on each template and how many sheets
// to print from each template, so that every variation's demand is met with the fewest printed sheets.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n_slots = instance.at("n_slots");
  int n_templates = instance.at("n_templates");
  int n_var = instance.at("n_var");
  std::vector<int> demand = instance.at("demand").get<std::vector<int>>();
  int max_demand = 0;
  for (int d : demand) if (d > max_demand) max_demand = d;

  // layout[t][v] = number of copies of variation v on template t
  vec<vec<IntVar*>> layout;
  for (int t = 0; t < n_templates; ++t) {
    layout.push();
    createVars(layout.last(), n_var, 0, n_slots);
  }

  // production[t] = number of sheets printed from template t
  // (never more than the largest demand: printing more is wasteful, so the optimum is within this bound)
  vec<IntVar*> production;
  createVars(production, n_templates, 0, max_demand);

  // each template has exactly n_slots slots, all of which carry a variation
  for (int t = 0; t < n_templates; ++t) {
    int_linear(layout[t], IRT_EQ, n_slots);
  }

  // the number of printed copies of each variation (sheets times copies per sheet, summed over
  // templates) must be at least its demand
  vec<vec<IntVar*>> printed;
  for (int t = 0; t < n_templates; ++t) {
    printed.push();
    for (int v = 0; v < n_var; ++v) {
      IntVar* p = newIntVar(0, max_demand * n_slots);
      int_times(production[t], layout[t][v], p);
      printed.last().push(p);
    }
  }
  vec<IntVar*> excess;
  for (int v = 0; v < n_var; ++v) {
    vec<IntVar*> col;
    for (int t = 0; t < n_templates; ++t) col.push(printed[t][v]);
    // printed copies = demand + excess (excess = overproduction of this variation)
    IntVar* e = newIntVar(0, n_slots * max_demand * n_templates);
    excess.push(e);
    col.push(e);
    vec<int> sign;
    for (int t = 0; t < n_templates; ++t) sign.push(1);
    sign.push(-1);
    int_linear(sign, col, IRT_EQ, demand[v]);
  }

  // minimize the total number of printed sheets
  IntVar* total = newIntVar(0, max_demand * n_templates);
  int_linear(production, IRT_EQ, total);

  // implied: every printed sheet carries n_slots copies, so the copies printed over all variations
  // equal n_slots times the total number of sheets
  {
    vec<IntVar*> all_printed;
    for (int t = 0; t < n_templates; ++t)
      for (int v = 0; v < n_var; ++v) all_printed.push(printed[t][v]);
    IntVar* copies = newIntVar(0, n_slots * max_demand * n_templates);
    vec<int> by_slots;
    vec<IntVar*> sheets;
    by_slots.push(n_slots);
    sheets.push(total);
    int_linear(by_slots, sheets, IRT_EQ, copies);
    int_linear(all_printed, IRT_EQ, copies);
  }

  vec<IntVar*> decisions;
  decisions.push(total);
  for (int t = 0; t < n_templates; ++t) decisions.push(production[t]);
  for (int t = 0; t < n_templates; ++t)
    for (int v = 0; v < n_var; ++v) decisions.push(layout[t][v]);
  branch(decisions, VAR_INORDER, VAL_MIN);
  optimize(total, OPT_MIN);

  json lay = json::array(), prod = json::array();
  for (int t = 0; t < n_templates; ++t) {
    json row = json::array();
    for (int v = 0; v < n_var; ++v) row.push_back(dcp::out(layout[t][v]));
    lay.push_back(row);
    prod.push_back(dcp::out(production[t]));
  }
  outputs = {{"layout", lay}, {"production", prod}};
}
