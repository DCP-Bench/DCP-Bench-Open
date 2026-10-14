#include <cstdint>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Curious set of integers (Martin Gardner, 1967): 1, 3, 8 and 120 have the
// property that the product of any two is one less than a perfect square. Find
// a further number, at least 0, that can join the set without destroying it.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();                    // size of the set
  const int64_t max_val = instance.at("max_val").get<int64_t>();  // upper bound on every member

  // The four known members are part of the puzzle statement, not the instance.
  const std::vector<int64_t> known = {1, 3, 8, 120};

  std::vector<IntVar> x;
  for (int i = 0; i < n; ++i) x.push_back(model.NewIntVar(Domain(0, max_val)));

  // The members are distinct.
  model.AddAllDifferent(x);

  // The set starts with the known members 1, 3, 8 and 120.
  for (int i = 0; i < n && i < static_cast<int>(known.size()); ++i) {
    model.AddEquality(x[i], known[i]);
  }

  // The product of any two members is one less than a perfect square:
  // root * root == x[i] * x[j] + 1, with the root bounded by max_val as in the
  // statement. The condition is symmetric in i and j, so each pair is posted once.
  for (int i = 0; i < n; ++i) {
    for (int j = i + 1; j < n; ++j) {
      const IntVar product = model.NewIntVar(Domain(0, max_val * max_val));
      model.AddMultiplicationEquality(product, {x[i], x[j]});
      const IntVar root = model.NewIntVar(Domain(0, max_val));
      const IntVar square = model.NewIntVar(Domain(0, max_val * max_val));
      model.AddMultiplicationEquality(square, {root, root});
      model.AddEquality(square, product + 1);
    }
  }

  // The number sought is the last member of the set.
  outputs = {{"number", x[n - 1].index()}};
}
