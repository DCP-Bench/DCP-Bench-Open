#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Langford's problem: arrange two copies of each of 1..k so that the pair
// labelled i is separated by exactly i places.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int k = instance.at("k").get<int>();
  const int len = 2 * k;

  std::vector<IntVar> position;
  for (int i = 0; i < len; ++i) {
    position.push_back(model.NewIntVar(Domain(0, len - 1)));
  }
  std::vector<IntVar> sol;
  for (int i = 0; i < len; ++i) sol.push_back(model.NewIntVar(Domain(1, k)));

  model.AddAllDifferent(position);

  // sol is read at a variable position, so both copies of each label need an
  // element constraint.
  const std::vector<LinearExpr> sol_exprs(sol.begin(), sol.end());
  for (int i = 1; i <= k; ++i) {
    model.AddEquality(position[i + k - 1], position[i - 1] + i + 1);

    IntVar first = model.NewIntVar(Domain(1, k));
    IntVar second = model.NewIntVar(Domain(1, k));
    model.AddElement(position[i - 1], sol_exprs, first);
    model.AddElement(position[k + i - 1], sol_exprs, second);
    model.AddEquality(first, i);
    model.AddEquality(second, i);
  }

  json out = json::array();
  for (const IntVar& s : sol) out.push_back(s.index());
  outputs = {{"sol", out}};
}
