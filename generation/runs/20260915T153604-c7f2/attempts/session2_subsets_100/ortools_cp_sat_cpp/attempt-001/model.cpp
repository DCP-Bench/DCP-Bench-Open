#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Split A into two disjoint non-empty subsets S and T with equal sums.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> a = instance.at("A").get<std::vector<int64_t>>();
  const int n = static_cast<int>(a.size());

  std::vector<BoolVar> in_s;
  std::vector<BoolVar> in_t;
  for (int i = 0; i < n; ++i) {
    in_s.push_back(model.NewBoolVar());
    in_t.push_back(model.NewBoolVar());
  }

  LinearExpr sum_s;
  LinearExpr sum_t;
  LinearExpr size_s;
  LinearExpr size_t;
  for (int i = 0; i < n; ++i) {
    sum_s += a[i] * in_s[i];
    sum_t += a[i] * in_t[i];
    size_s += in_s[i];
    size_t += in_t[i];
    // Disjointness: the reference writes sum(in_S * in_T) == 0, which is the
    // same as forbidding any element from landing in both subsets.
    model.AddLessOrEqual(in_s[i] + in_t[i], 1);
  }

  model.AddEquality(sum_s, sum_t);
  model.AddGreaterThan(size_s, 0);
  model.AddGreaterThan(size_t, 0);

  json s_out = json::array();
  json t_out = json::array();
  for (int i = 0; i < n; ++i) {
    s_out.push_back(in_s[i].index());
    t_out.push_back(in_t[i].index());
  }
  outputs = {{"in_S", s_out}, {"in_T", t_out}};
}
