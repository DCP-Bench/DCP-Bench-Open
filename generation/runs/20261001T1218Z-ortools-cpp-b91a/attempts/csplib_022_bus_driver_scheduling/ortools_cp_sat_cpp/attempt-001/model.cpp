#include <algorithm>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Bus driver scheduling: pick a set of shifts so that every piece of work is
// covered by exactly one chosen shift, using as few shifts as possible (every
// shift costs the same).
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int num_work = instance.at("num_work").get<int>();
  const int num_shifts = instance.at("num_shifts").get<int>();
  // shifts[i] lists the tasks that shift i covers.  The lists differ in length.
  const std::vector<std::vector<int>> shifts =
      instance.at("shifts").get<std::vector<std::vector<int>>>();

  // x[i] is true when shift i is selected.
  std::vector<BoolVar> x;
  for (int i = 0; i < num_shifts; ++i) x.push_back(model.NewBoolVar());

  // Each task is covered by exactly one selected shift (set partitioning).
  for (int t = 0; t < num_work; ++t) {
    LinearExpr selected_covering_t;
    for (int i = 0; i < num_shifts; ++i) {
      if (std::find(shifts[i].begin(), shifts[i].end(), t) != shifts[i].end()) {
        selected_covering_t += x[i];
      }
    }
    model.AddEquality(selected_covering_t, 1);
  }

  // Minimise the number of shifts used.
  LinearExpr shifts_used;
  for (int i = 0; i < num_shifts; ++i) shifts_used += x[i];
  model.Minimize(shifts_used);

  json x_out = json::array();
  for (const BoolVar& b : x) x_out.push_back(b.index());
  outputs = {{"x", x_out}};
}
