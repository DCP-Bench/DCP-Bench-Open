#include <algorithm>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Multicommodity transport: ship several products from origins to
// destinations, within per-product supply, per-pair capacity and demand, at
// minimum shipping cost.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<std::vector<int64_t>> supply =
      instance.at("supply").get<std::vector<std::vector<int64_t>>>();
  const std::vector<std::vector<int64_t>> demand =
      instance.at("demand").get<std::vector<std::vector<int64_t>>>();
  const std::vector<std::vector<int64_t>> limit =
      instance.at("limit").get<std::vector<std::vector<int64_t>>>();
  const std::vector<std::vector<std::vector<int64_t>>> cost =
      instance.at("cost")
          .get<std::vector<std::vector<std::vector<int64_t>>>>();

  const int n_origins = static_cast<int>(supply.size());
  const int n_destinations = static_cast<int>(demand.size());
  const int n_products = n_origins == 0 ? 0 : static_cast<int>(supply[0].size());

  int64_t max_supply = 0;
  int64_t supply_total = 0;
  for (const auto& row : supply) {
    for (const int64_t s : row) {
      max_supply = std::max(max_supply, s);
      supply_total += s;
    }
  }
  int64_t max_cost = 0;
  for (const auto& matrix : cost) {
    for (const auto& row : matrix) {
      for (const int64_t c : row) max_cost = std::max(max_cost, c);
    }
  }

  // x[i][j][p] is how much of product p travels from origin i to destination j.
  std::vector<std::vector<std::vector<IntVar>>> x(
      n_origins, std::vector<std::vector<IntVar>>(n_destinations));
  for (int i = 0; i < n_origins; ++i) {
    for (int j = 0; j < n_destinations; ++j) {
      for (int p = 0; p < n_products; ++p) {
        x[i][j].push_back(model.NewIntVar(Domain(0, max_supply)));
      }
    }
  }

  for (int i = 0; i < n_origins; ++i) {
    for (int p = 0; p < n_products; ++p) {
      LinearExpr shipped;
      for (int j = 0; j < n_destinations; ++j) shipped += x[i][j][p];
      model.AddLessOrEqual(shipped, supply[i][p]);
    }
  }
  for (int j = 0; j < n_destinations; ++j) {
    for (int p = 0; p < n_products; ++p) {
      LinearExpr received;
      for (int i = 0; i < n_origins; ++i) received += x[i][j][p];
      model.AddGreaterOrEqual(received, demand[j][p]);
    }
  }
  for (int i = 0; i < n_origins; ++i) {
    for (int j = 0; j < n_destinations; ++j) {
      LinearExpr on_route;
      for (int p = 0; p < n_products; ++p) on_route += x[i][j][p];
      model.AddLessOrEqual(on_route, limit[i][j]);
    }
  }

  LinearExpr freight;
  for (int i = 0; i < n_origins; ++i) {
    for (int j = 0; j < n_destinations; ++j) {
      for (int p = 0; p < n_products; ++p) {
        freight += cost[i][j][p] * x[i][j][p];
      }
    }
  }
  IntVar total_cost = model.NewIntVar(Domain(0, supply_total * max_cost));
  model.AddEquality(total_cost, freight);
  model.Minimize(total_cost);

  outputs = {{"total_cost", total_cost.index()}};
}
