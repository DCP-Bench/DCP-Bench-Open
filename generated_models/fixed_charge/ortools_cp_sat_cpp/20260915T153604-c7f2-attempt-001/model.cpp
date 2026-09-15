#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Fixed charge: a product can only be made on a rented machine.  Maximize
// sales profit minus the rent paid, within the labor and cloth capacities.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int num_machines = instance.at("num_machines").get<int>();
  const int num_products = instance.at("num_products").get<int>();
  const int64_t max_production = instance.at("max_production").get<int64_t>();
  const std::vector<int64_t> renting_cost =
      instance.at("renting_cost").get<std::vector<int64_t>>();
  const std::vector<int64_t> capacity =
      instance.at("capacity").get<std::vector<int64_t>>();
  const std::vector<int64_t> resources =
      instance.at("resources").get<std::vector<int64_t>>();
  const std::vector<std::vector<int64_t>> product =
      instance.at("product").get<std::vector<std::vector<int64_t>>>();
  const std::vector<std::vector<int64_t>> use =
      instance.at("use").get<std::vector<std::vector<int64_t>>>();

  std::vector<BoolVar> rent;
  for (int m = 0; m < num_machines; ++m) rent.push_back(model.NewBoolVar());
  std::vector<IntVar> produce;
  for (int p = 0; p < num_products; ++p) {
    produce.push_back(model.NewIntVar(Domain(0, max_production)));
  }
  // Profit bound 0..10000 is the reference's declared domain for z.
  IntVar z = model.NewIntVar(Domain(0, 10000));

  LinearExpr profit;
  for (int p = 0; p < num_products; ++p) profit += product[p][0] * produce[p];
  for (int m = 0; m < num_machines; ++m) profit -= renting_cost[m] * rent[m];
  model.AddEquality(z, profit);

  // Each resource column of `use` is consumed within its capacity.
  for (const int64_t r : resources) {
    LinearExpr used;
    for (int p = 0; p < num_products; ++p) {
      used += use[p][static_cast<int>(r)] * produce[p];
    }
    model.AddLessOrEqual(used, capacity[static_cast<int>(r)]);
  }

  // Nothing is produced on a machine that was not rented.  The reference
  // indexes `rent` by product index, which matches machine index here.
  for (int p = 0; p < num_products; ++p) {
    model.AddLessOrEqual(produce[p], max_production * rent[p]);
  }

  model.Maximize(z);
  outputs = {{"z", z.index()}};
}
