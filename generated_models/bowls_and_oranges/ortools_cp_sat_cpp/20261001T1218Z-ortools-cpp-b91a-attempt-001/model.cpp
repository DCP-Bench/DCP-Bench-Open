#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Bowls and oranges: put m oranges into n bowls in a line, at most one orange
// per bowl, so that no three oranges A, B, C have the distance from A to B
// equal to the distance from B to C.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();  // number of bowls
  const int m = instance.at("m").get<int>();  // number of oranges

  // x[i] is the bowl (1..n) holding orange i.
  std::vector<IntVar> x;
  for (int i = 0; i < m; ++i) x.push_back(model.NewIntVar(Domain(1, n)));

  // At most one orange per bowl.
  model.AddAllDifferent(x);

  // The oranges are listed in ascending order of bowl.
  for (int i = 1; i < m; ++i) model.AddLessOrEqual(x[i - 1], x[i]);

  // No three oranges A, B, C (taken in order) are equally spaced.
  for (int i = 0; i < m; ++i) {
    for (int j = i + 1; j < m; ++j) {
      for (int k = j + 1; k < m; ++k) {
        model.AddNotEqual(x[j] - x[i], x[k] - x[j]);
      }
    }
  }

  json x_out = json::array();
  for (const IntVar& v : x) x_out.push_back(v.index());
  outputs = {{"x", x_out}};
}
