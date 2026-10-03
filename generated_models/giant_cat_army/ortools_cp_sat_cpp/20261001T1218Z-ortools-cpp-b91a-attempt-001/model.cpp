#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Giant cat army riddle: start a list with 0 and extend it step by step by
// adding 5, adding 7 or taking the square root, so that 2, 10 and 14 appear in
// that order. All elements are distinct integers no larger than 60. Find such a
// list of length 24 ending with 14.
// The problem has no instance data; 60 and 24 come from the statement.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int maxval = 60;
  const int n = 24;

  std::vector<IntVar> x;
  for (int i = 0; i < n; ++i) x.push_back(model.NewIntVar(Domain(0, maxval)));

  // All elements are distinct.
  model.AddAllDifferent(x);

  // The list starts with 0, its first step adds 5 or 7, and it ends with 14.
  model.AddEquality(x[0], 0);
  model.AddLinearConstraint(x[1], Domain::FromValues({5, 7}));
  model.AddEquality(x[n - 1], 14);

  // Each step adds 5, adds 7, or takes the square root (the previous element is
  // the square of the next one).
  for (int i = 0; i + 1 < n; ++i) {
    const IntVar square = model.NewIntVar(Domain(0, maxval * maxval));
    model.AddMultiplicationEquality(square, {x[i + 1], x[i + 1]});
    const BoolVar add5 = model.NewBoolVar();
    const BoolVar add7 = model.NewBoolVar();
    const BoolVar root = model.NewBoolVar();
    model.AddEquality(x[i + 1], x[i] + 5).OnlyEnforceIf(add5);
    model.AddEquality(x[i + 1], x[i] + 7).OnlyEnforceIf(add7);
    model.AddEquality(x[i], square).OnlyEnforceIf(root);
    model.AddBoolOr({add5, add7, root});
  }

  // 2 appears before 10 (14 is last): positions ix2 < ix10 among 1..n-1, the
  // positions the list can index after the leading 0.
  std::vector<LinearExpr> elements(x.begin(), x.end());
  const IntVar ix2 = model.NewIntVar(Domain(1, n - 1));
  const IntVar ix10 = model.NewIntVar(Domain(1, n - 1));
  model.AddElement(ix2, elements, model.NewConstant(2));
  model.AddElement(ix10, elements, model.NewConstant(10));
  model.AddLessThan(ix2, ix10);

  json leaves = json::array();
  for (const IntVar& v : x) leaves.push_back(v.index());
  outputs = {{"x", leaves}};
}
