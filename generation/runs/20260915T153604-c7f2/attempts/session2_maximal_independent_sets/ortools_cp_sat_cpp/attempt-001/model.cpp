#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Maximal independent set: no edge has both ends selected, and no node could
// be added without breaking that.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();
  const std::vector<std::vector<int64_t>> adjacency_list =
      instance.at("adjacency_list").get<std::vector<std::vector<int64_t>>>();

  std::vector<BoolVar> nodes;
  for (int i = 0; i < n; ++i) nodes.push_back(model.NewBoolVar());

  // Independence.  The adjacency list is 1-based; each edge is seen from both
  // ends, so only i < j is posted.
  for (int i = 0; i < n; ++i) {
    for (const int64_t neighbor : adjacency_list[i]) {
      const int j = static_cast<int>(neighbor) - 1;
      if (i < j) model.AddLessOrEqual(nodes[i] + nodes[j], 1);
    }
  }

  // Maximality: every node is selected or has a selected neighbour.
  for (int i = 0; i < n; ++i) {
    std::vector<BoolVar> covered = {nodes[i]};
    for (const int64_t neighbor : adjacency_list[i]) {
      covered.push_back(nodes[static_cast<int>(neighbor) - 1]);
    }
    model.AddBoolOr(covered);
  }

  json out = json::array();
  for (const BoolVar& b : nodes) out.push_back(b.index());
  outputs = {{"nodes", out}};
}
