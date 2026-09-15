#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Bales of hay: every pair of bales was weighed, the pair weights arrived in
// sorted order with no record of which pair produced which weight.  Recover the
// individual bale weights.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();
  const std::vector<int64_t> weights =
      instance.at("weights").get<std::vector<int64_t>>();

  // Bale weight domain 0..50 is fixed by the problem statement, not by the
  // instance; the reference declares the same bound.
  std::vector<IntVar> bales;
  bales.reserve(n);
  for (int b = 0; b < n; ++b) bales.push_back(model.NewIntVar(Domain(0, 50)));

  // Each recorded weight is the sum of some pair i < j of distinct bales.
  for (const int64_t w : weights) {
    IntVar i = model.NewIntVar(Domain(0, n - 1));
    IntVar j = model.NewIntVar(Domain(0, n - 1));
    model.AddLessThan(i, j);

    IntVar bi = model.NewIntVar(Domain(0, 50));
    IntVar bj = model.NewIntVar(Domain(0, 50));
    model.AddElement(i, bales, bi);
    model.AddElement(j, bales, bj);
    model.AddEquality(bi + bj, w);
  }

  json bales_out = json::array();
  for (const IntVar& b : bales) bales_out.push_back(b.index());
  outputs = {{"bales", bales_out}};
}
