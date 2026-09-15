#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Three coins: flip exactly one coin per move and finish with every coin
// showing the same face.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int num_moves = instance.at("num_moves").get<int>();
  const std::vector<int64_t> init =
      instance.at("init").get<std::vector<int64_t>>();
  const int n = static_cast<int>(init.size());

  std::vector<std::vector<BoolVar>> steps(num_moves + 1);
  for (int m = 0; m <= num_moves; ++m) {
    for (int j = 0; j < n; ++j) steps[m].push_back(model.NewBoolVar());
  }

  for (int j = 0; j < n; ++j) model.AddEquality(steps[0][j], init[j]);

  // Exactly one coin differs between consecutive rows.
  for (int m = 1; m <= num_moves; ++m) {
    LinearExpr changes;
    for (int j = 0; j < n; ++j) {
      BoolVar differs = model.NewBoolVar();
      model.AddNotEqual(steps[m][j], steps[m - 1][j]).OnlyEnforceIf(differs);
      model.AddEquality(steps[m][j], steps[m - 1][j])
          .OnlyEnforceIf(differs.Not());
      changes += differs;
    }
    model.AddEquality(changes, 1);
  }

  // The final row is all heads or all tails.
  LinearExpr last;
  for (int j = 0; j < n; ++j) last += steps[num_moves][j];
  IntVar last_val = model.NewIntVar(Domain(0, n));
  model.AddEquality(last_val, last);
  model.AddLinearConstraint(last_val, Domain::FromValues({0, n}));

  json out = json::array();
  for (int m = 0; m <= num_moves; ++m) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(steps[m][j].index());
    out.push_back(row);
  }
  outputs = {{"steps", out}};
}
