#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Media selection: buy the cheapest set of advertising media that still
// reaches every target audience at least once.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> target_audiences =
      instance.at("target_audiences").get<std::vector<int64_t>>();
  const std::vector<int64_t> advertising_media =
      instance.at("advertising_media").get<std::vector<int64_t>>();
  const std::vector<std::vector<int64_t>> incidence =
      instance.at("incidence_matrix").get<std::vector<std::vector<int64_t>>>();
  const std::vector<int64_t> media_costs =
      instance.at("media_costs").get<std::vector<int64_t>>();
  const int num_audiences = static_cast<int>(target_audiences.size());
  const int num_media = static_cast<int>(advertising_media.size());

  std::vector<BoolVar> is_selected;
  for (int m = 0; m < num_media; ++m) is_selected.push_back(model.NewBoolVar());

  // Every audience must be reached by at least one selected medium.
  for (int t = 0; t < num_audiences; ++t) {
    LinearExpr reach;
    for (int m = 0; m < num_media; ++m) {
      reach += incidence[t][m] * is_selected[m];
    }
    model.AddGreaterOrEqual(reach, 1);
  }

  int64_t cost_total = 0;
  for (const int64_t c : media_costs) cost_total += c;
  LinearExpr spend;
  for (int m = 0; m < num_media; ++m) spend += media_costs[m] * is_selected[m];
  IntVar min_total_cost = model.NewIntVar(Domain(0, cost_total));
  model.AddEquality(min_total_cost, spend);
  model.Minimize(min_total_cost);

  json sel = json::array();
  for (const BoolVar& b : is_selected) sel.push_back(b.index());
  outputs = {{"is_selected", sel}, {"min_total_cost", min_total_cost.index()}};
}
