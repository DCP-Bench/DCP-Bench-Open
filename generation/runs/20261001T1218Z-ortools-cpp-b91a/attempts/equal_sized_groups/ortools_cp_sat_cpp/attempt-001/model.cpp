#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Equal sized groups: split a sorted list of n elements into k groups by
// choosing k-1 break points, keeping equal values in the same group, so that
// the group sizes are as close as possible to the ideal size round(n / k).
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> a = instance.at("a").get<std::vector<int64_t>>();
  const int k = instance.at("k").get<int>();
  const int n = static_cast<int>(a.size());

  // Ideal size of a group, round(n / k). Python's round() sends an exact .5 to
  // the even neighbour, so the same tie rule is applied here.
  int64_t gsize = n / k;
  const int64_t remainder = n % k;
  if (2 * remainder > k || (2 * remainder == k && gsize % 2 == 1)) ++gsize;

  // x[p] is the 1-based index of the p-th break point: the last element of
  // group p. Equal values must be in the same group, so no break point sits
  // between a[j-1] and a[j] when they are equal (1-based j = index of the
  // last element of the group). Removing those values from the domain of
  // each break point states exactly that.
  std::vector<int64_t> allowed;
  for (int j = 1; j <= n; ++j) {
    if (j == n || a[j - 1] != a[j]) allowed.push_back(j);
  }
  std::vector<IntVar> x;
  for (int p = 0; p < k - 1; ++p) x.push_back(model.NewIntVar(Domain::FromValues(allowed)));

  // s[i] is the number of elements in group i; every group is non-empty.
  std::vector<IntVar> s;
  for (int i = 0; i < k; ++i) s.push_back(model.NewIntVar(Domain(1, n)));

  // The first group's size is the index of the first break point.
  model.AddEquality(s[0], x[0]);
  // The size of a middle group is the difference between its two break points.
  for (int i = 1; i < k - 1; ++i) model.AddEquality(s[i], x[i] - x[i - 1]);
  // The last group holds whatever follows the last break point.
  model.AddEquality(s[k - 1], n - x[k - 2]);

  // z is the total error: how far each group size is from the ideal size.
  // Each deviation is at most n, so the sum is at most k * n.
  std::vector<IntVar> deviation;
  LinearExpr total_error;
  for (int i = 0; i < k; ++i) {
    const IntVar d = model.NewIntVar(Domain(0, n));
    model.AddAbsEquality(d, s[i] - gsize);
    deviation.push_back(d);
    total_error += d;
  }
  const IntVar z = model.NewIntVar(Domain(0, static_cast<int64_t>(k) * n));
  model.AddEquality(z, total_error);

  // Minimize the error.
  model.Minimize(z);

  json out = json::array();
  for (const IntVar& v : x) out.push_back(v.index());
  outputs = {{"x", out}};
}
