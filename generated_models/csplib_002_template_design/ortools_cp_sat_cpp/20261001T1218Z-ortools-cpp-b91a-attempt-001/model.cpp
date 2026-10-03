#include <algorithm>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Template design (CSPLib 2): choose, for each printing template, how many
// copies of each design variation it carries (filling all its slots) and how
// many sheets are printed from it, so that every variation's demand is met
// while the total number of printed sheets is as small as possible.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n_slots = instance.at("n_slots").get<int>();
  const int n_templates = instance.at("n_templates").get<int>();
  const int n_var = instance.at("n_var").get<int>();
  const std::vector<int64_t> demand = instance.at("demand").get<std::vector<int64_t>>();

  // Upper bound on the sheets printed from one template: the largest demand.
  const int64_t ub = *std::max_element(demand.begin(), demand.end());

  // production[i]: sheets printed from template i, between 1 and ub.
  std::vector<IntVar> production;
  for (int i = 0; i < n_templates; ++i) production.push_back(model.NewIntVar(Domain(1, ub)));

  // layout[i][v]: copies of variation v on template i, between 0 and n_var
  // (the domain the problem statement's model gives).
  std::vector<std::vector<IntVar>> layout(n_templates);
  for (int i = 0; i < n_templates; ++i)
    for (int v = 0; v < n_var; ++v) layout[i].push_back(model.NewIntVar(Domain(0, n_var)));

  // All slots of every template are populated.
  for (int i = 0; i < n_templates; ++i) {
    LinearExpr slots;
    for (int v = 0; v < n_var; ++v) slots += layout[i][v];
    model.AddEquality(slots, n_slots);
  }

  // Meet the demand of every variation: the copies printed over all templates,
  // production[i] * layout[i][v] summed over i, reach demand[v]. Each product
  // gets its own variable, since CP-SAT states products through
  // AddMultiplicationEquality.
  for (int v = 0; v < n_var; ++v) {
    LinearExpr printed;
    for (int i = 0; i < n_templates; ++i) {
      const IntVar copies = model.NewIntVar(Domain(0, ub * n_var));
      model.AddMultiplicationEquality(copies, {production[i], layout[i][v]});
      printed += copies;
    }
    model.AddGreaterOrEqual(printed, demand[v]);
  }

  // Implied: every template fills all its slots, so the sheets cover the total demand.
  LinearExpr sheets;
  for (int i = 0; i < n_templates; ++i) sheets += production[i];
  int64_t total_demand = 0;
  for (int64_t d : demand) total_demand += d;
  model.AddGreaterOrEqual(n_slots * sheets, total_demand);

  // Minimize the number of printed sheets.
  model.Minimize(sheets);

  json prod = json::array();
  for (const IntVar& p : production) prod.push_back(p.index());
  json lay = json::array();
  for (int i = 0; i < n_templates; ++i) {
    json row = json::array();
    for (int v = 0; v < n_var; ++v) row.push_back(layout[i][v].index());
    lay.push_back(row);
  }
  outputs = {{"production", prod}, {"layout", lay}};
}
