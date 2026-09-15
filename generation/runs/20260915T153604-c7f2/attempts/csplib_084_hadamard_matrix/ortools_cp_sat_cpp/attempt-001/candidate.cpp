#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

namespace {

// Periodic autocorrelation at shift s: sum_i arr[i] * arr[(i + s) mod l].
LinearExpr PeriodicAutocorrelation(CpModelBuilder& model,
                                   const std::vector<IntVar>& arr, int s) {
  const int l = static_cast<int>(arr.size());
  LinearExpr paf;
  for (int i = 0; i < l; ++i) {
    IntVar product = model.NewIntVar(Domain::FromValues({-1, 1}));
    model.AddMultiplicationEquality(product, {arr[i], arr[(i + s) % l]});
    paf += product;
  }
  return paf;
}

}  // namespace

// Hadamard matrix search: two +/-1 sequences whose autocorrelations sum to -2
// at every nonzero shift.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int l = instance.at("l").get<int>();
  const int m = (l - 1) / 2;

  // The reference declares the domain -1..1 and then excludes 0, which is the
  // same as allowing only the two values.
  const Domain pm_one = Domain::FromValues({-1, 1});
  std::vector<IntVar> a;
  std::vector<IntVar> b;
  for (int i = 0; i < l; ++i) {
    a.push_back(model.NewIntVar(pm_one));
    b.push_back(model.NewIntVar(pm_one));
  }

  LinearExpr sum_a;
  LinearExpr sum_b;
  for (int i = 0; i < l; ++i) {
    sum_a += a[i];
    sum_b += b[i];
  }
  model.AddEquality(sum_a, 1);
  model.AddEquality(sum_b, 1);

  for (int s = 1; s <= m; ++s) {
    model.AddEquality(PeriodicAutocorrelation(model, a, s) +
                          PeriodicAutocorrelation(model, b, s),
                      -2);
  }

  json a_out = json::array();
  for (const IntVar& v : a) a_out.push_back(v.index());
  json b_out = json::array();
  for (const IntVar& v : b) b_out.push_back(v.index());
  outputs = {{"a", a_out}, {"b", b_out}};
}
