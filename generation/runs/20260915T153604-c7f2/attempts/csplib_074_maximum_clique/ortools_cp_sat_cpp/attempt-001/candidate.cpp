#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Maximum clique: pick as many vertices as possible, no two of them
// non-adjacent.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();
  const std::vector<std::vector<int64_t>> adj =
      instance.at("adj").get<std::vector<std::vector<int64_t>>>();

  std::vector<BoolVar> c;
  for (int i = 0; i < n; ++i) c.push_back(model.NewBoolVar());

  for (int i = 0; i < n; ++i) {
    for (int j = i + 1; j < n; ++j) {
      if (adj[i][j] == 0) model.AddLessOrEqual(c[i] + c[j], 1);
    }
  }

  LinearExpr size;
  for (int i = 0; i < n; ++i) size += c[i];
  model.Maximize(size);

  json out = json::array();
  for (const BoolVar& b : c) out.push_back(b.index());
  outputs = {{"c", out}};
}
