#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Cutting stock: apply the available cutting patterns often enough to fill
// every order, using as few raw rolls as possible.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int num_patterns = instance.at("num_patterns").get<int>();
  const std::vector<std::vector<int64_t>> num_rolls_width =
      instance.at("num_rolls_width").get<std::vector<std::vector<int64_t>>>();
  const std::vector<int64_t> orders =
      instance.at("orders").get<std::vector<int64_t>>();
  const std::vector<int64_t> widths =
      instance.at("widths").get<std::vector<int64_t>>();
  const int num_item_widths = static_cast<int>(widths.size());

  // Usage bound 0..100 per pattern is the reference's declared domain.
  std::vector<IntVar> patterns_used;
  for (int j = 0; j < num_patterns; ++j) {
    patterns_used.push_back(model.NewIntVar(Domain(0, 100)));
  }

  for (int i = 0; i < num_item_widths; ++i) {
    LinearExpr cut;
    for (int j = 0; j < num_patterns; ++j) {
      cut += num_rolls_width[j][i] * patterns_used[j];
    }
    model.AddGreaterOrEqual(cut, orders[i]);
  }

  LinearExpr rolls;
  for (int j = 0; j < num_patterns; ++j) rolls += patterns_used[j];
  IntVar min_rolls_cut =
      model.NewIntVar(Domain(0, int64_t{100} * num_patterns));
  model.AddEquality(min_rolls_cut, rolls);
  model.Minimize(min_rolls_cut);

  json used = json::array();
  for (const IntVar& p : patterns_used) used.push_back(p.index());
  outputs = {{"patterns_used", used},
             {"min_rolls_cut", min_rolls_cut.index()}};
}
