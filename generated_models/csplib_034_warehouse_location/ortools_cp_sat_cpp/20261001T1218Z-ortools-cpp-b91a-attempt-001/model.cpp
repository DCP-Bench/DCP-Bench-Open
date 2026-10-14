#include <algorithm>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Warehouse location: decide which warehouses to open and which open warehouse
// supplies each store, within each warehouse's capacity, so that the cost of
// maintaining the open warehouses plus the cost of supplying the stores is minimal.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n_suppliers = instance.at("n_suppliers").get<int>();  // warehouses
  const int n_stores = instance.at("n_stores").get<int>();
  const int64_t building_cost = instance.at("building_cost").get<int64_t>();
  const std::vector<int64_t> capacity =
      instance.at("capacity").get<std::vector<int64_t>>();
  // cost_matrix[store][warehouse]: cost of supplying the store from the warehouse.
  const std::vector<std::vector<int64_t>> cost_matrix =
      instance.at("cost_matrix").get<std::vector<std::vector<int64_t>>>();

  // open_warehouses[w]: warehouse w is open.
  std::vector<BoolVar> open_warehouses;
  for (int w = 0; w < n_suppliers; ++w) {
    open_warehouses.push_back(model.NewBoolVar());
  }

  // supplier_assignment[s] is the warehouse that supplies store s.
  // supplied_by[s][w] is true exactly when supplier_assignment[s] == w; it is
  // the 0/1 form of the assignment, which keeps counts and costs linear.
  std::vector<IntVar> supplier_assignment;
  std::vector<std::vector<BoolVar>> supplied_by(n_stores);
  for (int s = 0; s < n_stores; ++s) {
    supplier_assignment.push_back(model.NewIntVar(Domain(0, n_suppliers - 1)));
    LinearExpr one_warehouse;
    LinearExpr warehouse_index;
    for (int w = 0; w < n_suppliers; ++w) {
      supplied_by[s].push_back(model.NewBoolVar());
      one_warehouse += supplied_by[s][w];
      warehouse_index += w * supplied_by[s][w];
    }
    model.AddEquality(one_warehouse, 1);
    model.AddEquality(supplier_assignment[s], warehouse_index);
  }

  // The number of stores assigned to a warehouse cannot exceed its capacity,
  // and a warehouse is open if and only if it supplies at least one store (so
  // stores are only assigned to open warehouses).
  for (int w = 0; w < n_suppliers; ++w) {
    LinearExpr stores_supplied;
    for (int s = 0; s < n_stores; ++s) stores_supplied += supplied_by[s][w];
    model.AddLessOrEqual(stores_supplied, capacity[w]);
    model.AddGreaterOrEqual(stores_supplied, 1).OnlyEnforceIf(open_warehouses[w]);
    model.AddEquality(stores_supplied, 0).OnlyEnforceIf(open_warehouses[w].Not());
  }

  // Total cost: the supply cost of every store plus the maintenance (building)
  // cost of every open warehouse.  The upper bound takes the dearest warehouse
  // for every store and opens all warehouses.
  LinearExpr supply_cost;
  int64_t cost_bound = building_cost * n_suppliers;
  for (int s = 0; s < n_stores; ++s) {
    for (int w = 0; w < n_suppliers; ++w) {
      supply_cost += cost_matrix[s][w] * supplied_by[s][w];
    }
    cost_bound += *std::max_element(cost_matrix[s].begin(), cost_matrix[s].end());
  }
  LinearExpr maintenance_cost;
  for (int w = 0; w < n_suppliers; ++w) {
    maintenance_cost += building_cost * open_warehouses[w];
  }
  IntVar total_cost = model.NewIntVar(Domain(0, cost_bound));
  model.AddEquality(total_cost, supply_cost + maintenance_cost);

  model.Minimize(total_cost);

  json open_out = json::array();
  for (const BoolVar& b : open_warehouses) open_out.push_back(b.index());
  json assignment_out = json::array();
  for (const IntVar& a : supplier_assignment) assignment_out.push_back(a.index());
  outputs = {{"total_cost", total_cost.index()},
             {"open_warehouses", open_out},
             {"supplier_assignment", assignment_out}};
}
