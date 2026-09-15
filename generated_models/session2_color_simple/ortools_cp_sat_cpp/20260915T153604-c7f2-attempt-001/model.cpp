#include <algorithm>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Map colouring: adjacent countries differ in colour, and the highest colour
// number used is as small as possible.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<std::vector<int64_t>> graph =
      instance.at("graph").get<std::vector<std::vector<int64_t>>>();

  // The instance carries only the edge list, so the country count is the
  // largest 1-based country id appearing in it.
  int64_t num_nodes = 0;
  for (const auto& edge : graph) {
    num_nodes = std::max({num_nodes, edge[0], edge[1]});
  }

  // Colours run 1..num_nodes, as in the reference.
  std::vector<IntVar> colors;
  for (int64_t i = 0; i < num_nodes; ++i) {
    colors.push_back(model.NewIntVar(Domain(1, num_nodes)));
  }

  for (const auto& edge : graph) {
    model.AddNotEqual(colors[edge[0] - 1], colors[edge[1] - 1]);
  }

  IntVar colors_used = model.NewIntVar(Domain(1, num_nodes));
  model.AddMaxEquality(colors_used,
                       std::vector<LinearExpr>(colors.begin(), colors.end()));
  model.Minimize(colors_used);

  json out = json::array();
  for (const IntVar& c : colors) out.push_back(c.index());
  outputs = {{"colors", out}};
}
