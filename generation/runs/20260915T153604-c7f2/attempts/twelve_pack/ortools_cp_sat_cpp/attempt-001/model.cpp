#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Twelve pack: buy whole packs to reach at least the target number of items,
// overshooting by as little as possible.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int64_t target = instance.at("target").get<int64_t>();
  const std::vector<int64_t> packs =
      instance.at("packs").get<std::vector<int64_t>>();
  const int n = static_cast<int>(packs.size());

  // Pack-count ceiling of 2 * target follows the reference's max_val.
  const int64_t max_val = target * 2;
  std::vector<IntVar> counts;
  for (int i = 0; i < n; ++i) counts.push_back(model.NewIntVar(Domain(0, max_val)));

  IntVar total = model.NewIntVar(Domain(0, max_val * n));
  LinearExpr items;
  for (int i = 0; i < n; ++i) items += packs[i] * counts[i];
  model.AddEquality(total, items);
  model.AddGreaterOrEqual(total, target);
  model.Minimize(total);

  json out = json::array();
  for (const IntVar& c : counts) out.push_back(c.index());
  outputs = {{"counts", out}};
}
