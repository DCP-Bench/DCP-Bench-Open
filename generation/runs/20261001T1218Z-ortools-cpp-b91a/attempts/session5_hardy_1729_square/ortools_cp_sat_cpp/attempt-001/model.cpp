#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Hardy 1729, squares version: four different numbers a, b, c, d between 1 and
// 100 with a^2 + b^2 = c^2 + d^2.
// The problem has no instance data; the range 1..100 comes from the statement.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int range_min = 1;
  const int range_max = 100;
  std::vector<IntVar> v;
  std::vector<IntVar> sq;  // sq[k] is the square of v[k]
  for (int k = 0; k < 4; ++k) {
    v.push_back(model.NewIntVar(Domain(range_min, range_max)));
    sq.push_back(model.NewIntVar(Domain(range_min * range_min, range_max * range_max)));
    model.AddMultiplicationEquality(sq[k], {v[k], v[k]});
  }

  // The sum of the squares of the first two equals that of the other two.
  model.AddEquality(sq[0] + sq[1], sq[2] + sq[3]);

  // The four numbers are all different.
  model.AddAllDifferent(v);

  outputs = {{"a", v[0].index()}, {"b", v[1].index()}, {"c", v[2].index()}, {"d", v[3].index()}};
}
