#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Number partitioning: split 1..n into two halves with equal sums and equal
// sums of squares.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();
  const int half = n / 2;

  std::vector<IntVar> a;
  std::vector<IntVar> b;
  for (int i = 0; i < half; ++i) {
    a.push_back(model.NewIntVar(Domain(1, n)));
    b.push_back(model.NewIntVar(Domain(1, n)));
  }

  std::vector<IntVar> everything(a);
  everything.insert(everything.end(), b.begin(), b.end());
  model.AddAllDifferent(everything);

  LinearExpr sum_a;
  LinearExpr sum_b;
  LinearExpr squares_a;
  LinearExpr squares_b;
  for (int i = 0; i < half; ++i) {
    sum_a += a[i];
    sum_b += b[i];
    IntVar sq_a = model.NewIntVar(Domain(1, int64_t{n} * n));
    IntVar sq_b = model.NewIntVar(Domain(1, int64_t{n} * n));
    model.AddMultiplicationEquality(sq_a, {a[i], a[i]});
    model.AddMultiplicationEquality(sq_b, {b[i], b[i]});
    squares_a += sq_a;
    squares_b += sq_b;
  }
  model.AddEquality(sum_a, sum_b);
  model.AddEquality(squares_a, squares_b);

  json a_out = json::array();
  for (const IntVar& v : a) a_out.push_back(v.index());
  json b_out = json::array();
  for (const IntVar& v : b) b_out.push_back(v.index());
  outputs = {{"A", a_out}, {"B", b_out}};
}
