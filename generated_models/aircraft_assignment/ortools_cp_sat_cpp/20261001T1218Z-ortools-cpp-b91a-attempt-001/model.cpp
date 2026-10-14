#include <algorithm>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Aircraft assignment: decide how many aircraft of each type fly each route so
// that every route's passenger demand is met, no type is used beyond the number
// of aircraft available, and the total operating cost is as low as possible.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> availability =
      instance.at("availability").get<std::vector<int64_t>>();
  const std::vector<int64_t> demand =
      instance.at("demand").get<std::vector<int64_t>>();
  // capabilities[i][j]: passengers one aircraft of type i carries on route j.
  const std::vector<std::vector<int64_t>> capabilities =
      instance.at("capabilities").get<std::vector<std::vector<int64_t>>>();
  // costs[i][j]: cost of assigning one aircraft of type i to route j.
  const std::vector<std::vector<int64_t>> costs =
      instance.at("costs").get<std::vector<std::vector<int64_t>>>();
  const int num_aircraft = static_cast<int>(availability.size());
  const int num_routes = static_cast<int>(demand.size());

  // allocation[i][j]: number of aircraft of type i assigned to route j.  No
  // type can put more aircraft on one route than the largest fleet available,
  // which is the domain the reference declares.
  const int64_t max_fleet =
      *std::max_element(availability.begin(), availability.end());
  std::vector<std::vector<IntVar>> allocation(num_aircraft);
  for (int i = 0; i < num_aircraft; ++i) {
    for (int j = 0; j < num_routes; ++j) {
      allocation[i].push_back(model.NewIntVar(Domain(0, max_fleet)));
    }
  }

  // The aircraft of a type assigned across all routes cannot exceed the
  // number of aircraft of that type available.
  for (int i = 0; i < num_aircraft; ++i) {
    LinearExpr used;
    for (int j = 0; j < num_routes; ++j) used += allocation[i][j];
    model.AddLessOrEqual(used, availability[i]);
  }

  // Each route's passenger demand must be met by the capacity assigned to it.
  for (int j = 0; j < num_routes; ++j) {
    LinearExpr capacity_on_route;
    for (int i = 0; i < num_aircraft; ++i) {
      capacity_on_route += capabilities[i][j] * allocation[i][j];
    }
    model.AddGreaterOrEqual(capacity_on_route, demand[j]);
  }

  // Minimise the total operating cost of the assignment.
  LinearExpr total_cost;
  for (int i = 0; i < num_aircraft; ++i) {
    for (int j = 0; j < num_routes; ++j) {
      total_cost += costs[i][j] * allocation[i][j];
    }
  }
  model.Minimize(total_cost);

  json out = json::array();
  for (int i = 0; i < num_aircraft; ++i) {
    json row = json::array();
    for (int j = 0; j < num_routes; ++j) row.push_back(allocation[i][j].index());
    out.push_back(row);
  }
  outputs = {{"allocation", out}};
}
