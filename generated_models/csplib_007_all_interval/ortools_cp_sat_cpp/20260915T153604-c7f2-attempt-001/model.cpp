#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// All-interval series: a permutation of the pitch classes whose successive
// absolute differences are themselves all distinct.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();

  std::vector<IntVar> x;
  for (int i = 0; i < n; ++i) x.push_back(model.NewIntVar(Domain(0, n - 1)));
  std::vector<IntVar> diffs;
  for (int i = 0; i < n - 1; ++i) {
    diffs.push_back(model.NewIntVar(Domain(1, n - 1)));
  }

  model.AddAllDifferent(x);
  model.AddAllDifferent(diffs);

  for (int i = 0; i < n - 1; ++i) {
    model.AddAbsEquality(diffs[i], x[i + 1] - x[i]);
  }

  json x_out = json::array();
  for (const IntVar& xi : x) x_out.push_back(xi.index());
  json d_out = json::array();
  for (const IntVar& d : diffs) d_out.push_back(d.index());
  outputs = {{"x", x_out}, {"diffs", d_out}};
}
