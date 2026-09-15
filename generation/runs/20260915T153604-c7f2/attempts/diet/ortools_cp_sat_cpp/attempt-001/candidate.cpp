#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Diet: buy whole servings of each food so that every nutritional requirement
// is met at least, at minimum total cost.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();
  const std::vector<int64_t> price =
      instance.at("price").get<std::vector<int64_t>>();
  const std::vector<int64_t> limits =
      instance.at("limits").get<std::vector<int64_t>>();

  // The nutrition table belongs to the problem statement, not to the instance:
  // the reference fixes these same four rows (calories, chocolate, sugar, fat)
  // for the four foods, and only prices and requirements vary.
  const std::vector<std::vector<int64_t>> nutrition = {
      {400, 200, 150, 500},  // calories
      {3, 2, 0, 0},          // chocolate
      {2, 2, 4, 4},          // sugar
      {2, 4, 1, 5},          // fat
  };

  // Serving counts and cost keep the reference's declared bounds.
  std::vector<IntVar> x;
  x.reserve(n);
  for (int i = 0; i < n; ++i) x.push_back(model.NewIntVar(Domain(0, 10000)));
  IntVar cost = model.NewIntVar(Domain(0, 1000));

  for (int k = 0; k < static_cast<int>(nutrition.size()); ++k) {
    LinearExpr amount;
    for (int i = 0; i < n; ++i) amount += nutrition[k][i] * x[i];
    model.AddGreaterOrEqual(amount, limits[k]);
  }

  LinearExpr spend;
  for (int i = 0; i < n; ++i) spend += price[i] * x[i];
  model.AddEquality(cost, spend);
  model.Minimize(cost);

  outputs = {{"cost", cost.index()}};
}
