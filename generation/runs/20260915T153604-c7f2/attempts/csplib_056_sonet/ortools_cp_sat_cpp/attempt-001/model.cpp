#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// SONET ring assignment: put every communicating pair of nodes on a shared
// ring, within each ring's node capacity, using as few add-drop multiplexers
// as possible.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int r = instance.at("r").get<int>();
  const int n = instance.at("n").get<int>();
  const std::vector<std::vector<int64_t>> demand =
      instance.at("demand").get<std::vector<std::vector<int64_t>>>();
  const std::vector<int64_t> capacity_nodes =
      instance.at("capacity_nodes").get<std::vector<int64_t>>();

  std::vector<std::vector<BoolVar>> ring_config(r);
  for (int k = 0; k < r; ++k) {
    for (int i = 0; i < n; ++i) ring_config[k].push_back(model.NewBoolVar());
  }

  // Nodes with traffic between them must meet on some ring.
  for (int i = 0; i < n; ++i) {
    for (int j = i + 1; j < n; ++j) {
      if (demand[i][j] <= 0) continue;
      LinearExpr shared;
      for (int k = 0; k < r; ++k) {
        BoolVar both = model.NewBoolVar();
        model.AddBoolAnd({ring_config[k][i], ring_config[k][j]})
            .OnlyEnforceIf(both);
        model.AddBoolOr({ring_config[k][i].Not(), ring_config[k][j].Not()})
            .OnlyEnforceIf(both.Not());
        shared += both;
      }
      model.AddGreaterOrEqual(shared, 1);
    }
  }

  for (int k = 0; k < r; ++k) {
    LinearExpr on_ring;
    for (int i = 0; i < n; ++i) on_ring += ring_config[k][i];
    model.AddLessOrEqual(on_ring, capacity_nodes[k]);
  }

  // One multiplexer per node-to-ring assignment.
  LinearExpr adms;
  for (int k = 0; k < r; ++k) {
    for (int i = 0; i < n; ++i) adms += ring_config[k][i];
  }
  IntVar total_adms = model.NewIntVar(Domain(0, int64_t{r} * n));
  model.AddEquality(total_adms, adms);
  model.Minimize(total_adms);

  json out = json::array();
  for (int k = 0; k < r; ++k) {
    json row = json::array();
    for (int i = 0; i < n; ++i) row.push_back(ring_config[k][i].index());
    out.push_back(row);
  }
  outputs = {{"ring_config", out}, {"total_adms", total_adms.index()}};
}
