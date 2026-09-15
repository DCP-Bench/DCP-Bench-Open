#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Facility location: open warehouses and ship from them to the regions at
// minimum total cost, subject to the company's siting rules.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<std::string> warehouse_s =
      instance.at("warehouse_s").get<std::vector<std::string>>();
  const std::vector<int64_t> fixed_costs =
      instance.at("fixed_costs").get<std::vector<int64_t>>();
  const int64_t max_shipping = instance.at("max_shipping").get<int64_t>();
  const std::vector<int64_t> demands =
      instance.at("demands").get<std::vector<int64_t>>();
  const std::vector<std::vector<int64_t>> costs =
      instance.at("shipping_costs").get<std::vector<std::vector<int64_t>>>();
  const int num_companies = static_cast<int>(warehouse_s.size());
  const int num_regions = static_cast<int>(demands.size());

  // The siting rules name warehouses by position, exactly as the reference
  // unpacks them: New York, Los Angeles, Chicago, Atlanta.
  const int new_york = 0;
  const int los_angeles = 1;
  const int atlanta = 3;

  std::vector<BoolVar> open_warehouse;
  for (int i = 0; i < num_companies; ++i) {
    open_warehouse.push_back(model.NewBoolVar());
  }
  std::vector<std::vector<IntVar>> ships(num_companies);
  for (int i = 0; i < num_companies; ++i) {
    for (int j = 0; j < num_regions; ++j) {
      ships[i].push_back(model.NewIntVar(Domain(0, max_shipping)));
    }
  }
  // total_cost keeps the reference's declared 0..10000 domain.
  IntVar total_cost = model.NewIntVar(Domain(0, 10000));

  // A warehouse ships nothing unless it is open, and never more than its cap.
  for (int i = 0; i < num_companies; ++i) {
    LinearExpr out_of_warehouse;
    for (int j = 0; j < num_regions; ++j) out_of_warehouse += ships[i][j];
    model.AddLessOrEqual(out_of_warehouse, max_shipping * open_warehouse[i]);
  }

  for (int j = 0; j < num_regions; ++j) {
    LinearExpr into_region;
    for (int i = 0; i < num_companies; ++i) into_region += ships[i][j];
    model.AddGreaterOrEqual(into_region, demands[j]);
  }

  LinearExpr spend;
  for (int i = 0; i < num_companies; ++i) {
    spend += fixed_costs[i] * open_warehouse[i];
    for (int j = 0; j < num_regions; ++j) spend += costs[i][j] * ships[i][j];
  }
  model.AddEquality(total_cost, spend);

  // Opening New York requires opening Los Angeles.
  model.AddImplication(open_warehouse[new_york], open_warehouse[los_angeles]);
  // At most three warehouses open.
  LinearExpr opened;
  for (int i = 0; i < num_companies; ++i) opened += open_warehouse[i];
  model.AddLessOrEqual(opened, 3);
  // Atlanta or Los Angeles must be open.
  model.AddBoolOr({open_warehouse[atlanta], open_warehouse[los_angeles]});

  model.Minimize(total_cost);

  json open_out = json::array();
  for (const BoolVar& b : open_warehouse) open_out.push_back(b.index());
  json ships_out = json::array();
  for (int i = 0; i < num_companies; ++i) {
    json row = json::array();
    for (int j = 0; j < num_regions; ++j) row.push_back(ships[i][j].index());
    ships_out.push_back(row);
  }
  outputs = {{"total_cost", total_cost.index()},
             {"open_warehouse", open_out},
             {"ships", ships_out}};
}
