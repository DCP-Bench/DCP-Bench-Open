#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Appointment scheduling: give every person exactly one slot, every slot
// exactly one person, and only where the free-busy matrix allows it.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<std::vector<int64_t>> m =
      instance.at("m").get<std::vector<std::vector<int64_t>>>();
  const int n = static_cast<int>(m.size());

  std::vector<std::vector<BoolVar>> x(n);
  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) x[i].push_back(model.NewBoolVar());
  }

  for (int i = 0; i < n; ++i) {
    // The slot person i takes must be one they are free for.
    LinearExpr free_slot;
    for (int j = 0; j < n; ++j) free_slot += m[i][j] * x[i][j];
    model.AddEquality(free_slot, 1);

    // One slot per person, and one person per slot.
    LinearExpr row;
    LinearExpr col;
    for (int j = 0; j < n; ++j) {
      row += x[i][j];
      col += x[j][i];
    }
    model.AddEquality(row, 1);
    model.AddEquality(col, 1);
  }

  json out = json::array();
  for (int i = 0; i < n; ++i) {
    json r = json::array();
    for (int j = 0; j < n; ++j) r.push_back(x[i][j].index());
    out.push_back(r);
  }
  outputs = {{"x", out}};
}
