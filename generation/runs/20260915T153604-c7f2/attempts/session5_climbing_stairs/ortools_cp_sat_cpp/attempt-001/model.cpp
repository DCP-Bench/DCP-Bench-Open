#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Climbing stairs: split n steps into moves of m1..m2 steps each.  Unused
// moves are zero, and once a move is zero every later one is zero too.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();
  const int64_t m1 = instance.at("m1").get<int64_t>();
  const int64_t m2 = instance.at("m2").get<int64_t>();

  std::vector<IntVar> steps;
  for (int i = 0; i < n; ++i) steps.push_back(model.NewIntVar(Domain(0, m2)));

  LinearExpr climbed;
  for (int i = 0; i < n; ++i) climbed += steps[i];
  model.AddEquality(climbed, n);

  // A move is either skipped or a stride of at least m1 and at most m2.
  std::vector<BoolVar> is_zero;
  for (int i = 0; i < n; ++i) {
    BoolVar zero = model.NewBoolVar();
    model.AddEquality(steps[i], 0).OnlyEnforceIf(zero);
    model.AddGreaterOrEqual(steps[i], m1).OnlyEnforceIf(zero.Not());
    model.AddLessOrEqual(steps[i], m2);
    is_zero.push_back(zero);
  }

  // Trailing zeros: a zero move forces every later move to zero as well.
  for (int i = 1; i < n; ++i) {
    for (int j = i; j < n; ++j) {
      model.AddEquality(steps[j], 0).OnlyEnforceIf(is_zero[i - 1]);
    }
  }

  json out = json::array();
  for (const IntVar& s : steps) out.push_back(s.index());
  outputs = {{"steps", out}};
}
