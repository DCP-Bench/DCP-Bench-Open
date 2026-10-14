#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Clock triplets: rearrange the numbers 1..12 on a clock face so that no three
// adjacent numbers (going round the circle) sum to more than 21.
// The problem has no instance data: the twelve numbers and the bound 21 are
// part of the puzzle.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int n = 12;
  // x[i]: the number at position i on the clock face.
  std::vector<IntVar> x;
  for (int i = 0; i < n; ++i) x.push_back(model.NewIntVar(Domain(1, n)));
  // triplet_sum: an upper bound on every triplet sum, at most 21.
  const IntVar triplet_sum = model.NewIntVar(Domain(0, 21));

  // Each number appears once.
  model.AddAllDifferent(x);

  // Every three adjacent numbers, wrapping round the clock, sum to at most triplet_sum.
  for (int i = 0; i < n; ++i)
    model.AddLessOrEqual(x[i] + x[(i + n - 1) % n] + x[(i + n - 2) % n], triplet_sum);

  json out = json::array();
  for (const IntVar& v : x) out.push_back(v.index());
  outputs = {{"x", out}};
}
