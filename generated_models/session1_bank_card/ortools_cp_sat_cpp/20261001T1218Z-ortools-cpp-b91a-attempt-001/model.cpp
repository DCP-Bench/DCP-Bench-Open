#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Bank card PIN: a four-digit PIN abcd whose digits are all different, where
// the two-digit number cd is 3 times ab and da is 2 times bc.
// The problem has no instance data.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  // The four digits of the PIN.
  const IntVar a = model.NewIntVar(Domain(0, 9));
  const IntVar b = model.NewIntVar(Domain(0, 9));
  const IntVar c = model.NewIntVar(Domain(0, 9));
  const IntVar d = model.NewIntVar(Domain(0, 9));

  // No two digits are the same.
  model.AddAllDifferent(std::vector<IntVar>{a, b, c, d});

  // The two-digit number cd is 3 times the two-digit number ab.
  model.AddEquality(10 * c + d, 3 * (10 * a + b));

  // The two-digit number da is 2 times the two-digit number bc.
  model.AddEquality(10 * d + a, 2 * (10 * b + c));

  outputs = {{"a", a.index()}, {"b", b.index()}, {"c", c.index()}, {"d", d.index()}};
}
