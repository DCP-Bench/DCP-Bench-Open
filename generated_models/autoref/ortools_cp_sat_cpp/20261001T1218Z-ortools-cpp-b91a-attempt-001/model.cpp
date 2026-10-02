#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Autoref: find a series s[0..n+1] in which every i from 0 to n occurs exactly
// s[i] times, and whose last element s[n+1] equals m.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();
  const int64_t m = instance.at("m").get<int64_t>();
  const int length = n + 2;  // s0, s1, ..., sn, sn+1

  // Every element of the series takes a value from 0 to n.
  // has_value[k][v] is true exactly when s[k] == v; each element has exactly
  // one value, so s[k] is the sum of v * has_value[k][v].  This one-hot form
  // makes the occurrence counts below plain sums.
  std::vector<IntVar> s;
  std::vector<std::vector<BoolVar>> has_value(length);
  for (int k = 0; k < length; ++k) {
    s.push_back(model.NewIntVar(Domain(0, n)));
    LinearExpr one_value;
    LinearExpr value_of_k;
    for (int v = 0; v <= n; ++v) {
      has_value[k].push_back(model.NewBoolVar());
      one_value += has_value[k][v];
      value_of_k += v * has_value[k][v];
    }
    model.AddEquality(one_value, 1);
    model.AddEquality(s[k], value_of_k);
  }

  // The last element is m.
  model.AddEquality(s[n + 1], m);

  // There are s[i] occurrences of i in the series, for each i from 0 to n.
  for (int i = 0; i <= n; ++i) {
    LinearExpr occurrences_of_i;
    for (int k = 0; k < length; ++k) occurrences_of_i += has_value[k][i];
    model.AddEquality(s[i], occurrences_of_i);
  }

  json s_out = json::array();
  for (const IntVar& v : s) s_out.push_back(v.index());
  outputs = {{"s", s_out}};
}
