#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Candies: every child gets at least one candy, and between neighbours the
// higher-rated child gets strictly more.  Minimize the total handed out.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> ratings =
      instance.at("ratings").get<std::vector<int64_t>>();
  const int n = static_cast<int>(ratings.size());

  // Bounds follow the reference: at least one and at most n candies each.
  std::vector<IntVar> x;
  x.reserve(n);
  for (int i = 0; i < n; ++i) x.push_back(model.NewIntVar(Domain(1, n)));
  IntVar z = model.NewIntVar(Domain(1, static_cast<int64_t>(n) * n));

  LinearExpr total;
  for (int i = 0; i < n; ++i) total += x[i];
  model.AddEquality(z, total);
  model.AddGreaterOrEqual(z, n);

  for (int i = 1; i < n; ++i) {
    if (ratings[i - 1] > ratings[i]) {
      model.AddGreaterThan(x[i - 1], x[i]);
    } else if (ratings[i - 1] < ratings[i]) {
      model.AddLessThan(x[i - 1], x[i]);
    }
  }

  model.Minimize(z);

  json x_out = json::array();
  for (const IntVar& xi : x) x_out.push_back(xi.index());
  outputs = {{"z", z.index()}, {"x", x_out}};
}
