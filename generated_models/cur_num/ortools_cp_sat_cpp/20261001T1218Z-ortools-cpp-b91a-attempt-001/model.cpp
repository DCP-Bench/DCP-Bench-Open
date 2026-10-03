#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Curious numbers (Dudeney, Amusements in Mathematics 114): 48 plus 1 is a
// square and half of 48 plus 1 is a square too. Find another number between
// 1 and 10000 with this peculiarity.
// The problem has no instance data; the range 1..10000 and the excluded 48
// come from the problem statement.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const Domain range(1, 10000);
  const IntVar peculiar = model.NewIntVar(range);  // the number sought
  const IntVar a = model.NewIntVar(range);         // the number plus 1
  const IntVar b = model.NewIntVar(range);         // square root of a
  const IntVar c = model.NewIntVar(range);         // half of the number
  const IntVar d = model.NewIntVar(range);         // the half plus 1
  const IntVar e = model.NewIntVar(range);         // square root of d

  // 48 is already known, so look for another number.
  model.AddNotEqual(peculiar, 48);

  // Adding 1 to the number gives a square.
  model.AddEquality(peculiar + 1, a);
  model.AddMultiplicationEquality(a, {b, b});

  // Adding 1 to its half also gives a square.
  model.AddEquality(peculiar, 2 * c);
  model.AddEquality(c + 1, d);
  model.AddMultiplicationEquality(d, {e, e});

  outputs = {{"peculiar", peculiar.index()}};
}
