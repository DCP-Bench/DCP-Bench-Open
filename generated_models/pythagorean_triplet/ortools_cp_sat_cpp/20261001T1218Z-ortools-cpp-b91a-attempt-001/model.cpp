#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Special Pythagorean triplet (Project Euler 9): natural numbers a, b, c with
// a^2 + b^2 = c^2 and a + b + c = 1000.
// The problem has no instance data. Each number is at most 500, the bound the
// statement's model uses (c < a + b, so c < 500).
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const Domain range(1, 500);
  const IntVar a = model.NewIntVar(range);
  const IntVar b = model.NewIntVar(range);
  const IntVar c = model.NewIntVar(range);

  // The three numbers add up to 1000.
  model.AddEquality(a + b + c, 1000);

  // a^2 + b^2 = c^2, with each square in its own product variable.
  const Domain squares(1, 250000);
  const IntVar a2 = model.NewIntVar(squares);
  const IntVar b2 = model.NewIntVar(squares);
  const IntVar c2 = model.NewIntVar(squares);
  model.AddMultiplicationEquality(a2, {a, a});
  model.AddMultiplicationEquality(b2, {b, b});
  model.AddMultiplicationEquality(c2, {c, c});
  model.AddEquality(a2 + b2, c2);

  outputs = {{"a", a.index()}, {"b", b.index()}, {"c", c.index()}};
}
