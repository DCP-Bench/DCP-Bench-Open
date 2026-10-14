#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Ages of the sons: the product of three sons' ages is 36; knowing also their
// sum still leaves the mathematician unsure, so another triple with product 36
// has the same sum; "the oldest son" then tells him there is a single oldest.
// The problem has no instance data: 36 and the age bounds are part of the puzzle.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int64_t product = 36;

  // A1 >= A2 >= A3 are the sons' ages, oldest first; B1 >= B2 >= B3 is the
  // other triple the mathematician could not rule out.
  const IntVar A1 = model.NewIntVar(Domain(0, product));
  const IntVar A2 = model.NewIntVar(Domain(0, product));
  const IntVar A3 = model.NewIntVar(Domain(0, product));
  const IntVar B1 = model.NewIntVar(Domain(0, product));
  const IntVar B2 = model.NewIntVar(Domain(0, product));
  const IntVar B3 = model.NewIntVar(Domain(0, product));

  // There is a single oldest son (blue eyes), and the ages are listed in
  // decreasing order.
  model.AddGreaterThan(A1, A2);
  model.AddGreaterOrEqual(A2, A3);

  // The product of the ages is 36 (built two factors at a time).
  const IntVar a12 = model.NewIntVar(Domain(0, product * product));
  model.AddMultiplicationEquality(a12, {A1, A2});
  model.AddMultiplicationEquality(model.NewConstant(product), {a12, A3});

  // The alternative triple, also in decreasing order, with a different oldest
  // age and the same product.
  model.AddGreaterOrEqual(B1, B2);
  model.AddGreaterOrEqual(B2, B3);
  model.AddNotEqual(A1, B1);
  const IntVar b12 = model.NewIntVar(Domain(0, product * product));
  model.AddMultiplicationEquality(b12, {B1, B2});
  model.AddMultiplicationEquality(model.NewConstant(product), {b12, B3});

  // Both triples have the same sum (the number of windows), which is why the
  // sum alone was not enough.
  model.AddEquality(A1 + A2 + A3, B1 + B2 + B3);

  outputs = {{"A1", A1.index()}, {"A2", A2.index()}, {"A3", A3.index()}};
}
