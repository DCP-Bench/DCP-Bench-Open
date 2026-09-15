#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Low-autocorrelation binary sequence: a +/-1 sequence minimizing the sum of
// squared periodic autocorrelations.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();

  // The reference declares -1..1 and then excludes 0, leaving the two values.
  const Domain pm_one = Domain::FromValues({-1, 1});
  std::vector<IntVar> sequence;
  for (int i = 0; i < n; ++i) sequence.push_back(model.NewIntVar(pm_one));

  LinearExpr energy;
  for (int s = 1; s < n; ++s) {
    LinearExpr paf;
    for (int i = 0; i < n; ++i) {
      IntVar product = model.NewIntVar(pm_one);
      model.AddMultiplicationEquality(product,
                                      {sequence[i], sequence[(i + s) % n]});
      paf += product;
    }
    IntVar paf_var = model.NewIntVar(Domain(-n, n));
    model.AddEquality(paf_var, paf);
    IntVar squared = model.NewIntVar(Domain(0, int64_t{n} * n));
    model.AddMultiplicationEquality(squared, {paf_var, paf_var});
    energy += squared;
  }

  IntVar total_energy =
      model.NewIntVar(Domain(0, int64_t{n} * n * (n > 0 ? n - 1 : 0)));
  model.AddEquality(total_energy, energy);
  model.Minimize(total_energy);

  json out = json::array();
  for (const IntVar& s : sequence) out.push_back(s.index());
  outputs = {{"sequence", out}};
}
