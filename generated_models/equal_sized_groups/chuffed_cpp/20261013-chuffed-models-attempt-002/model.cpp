// Equal sized groups: split a sorted list into k groups by k-1 break points, keeping equal values together and group sizes close to round(N/k).
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> a = instance.at("a").get<std::vector<int>>();
  int k = instance.at("k");
  int N = static_cast<int>(a.size());
  int target = (2 * N + k) / (2 * k);  // round(N/k), the ideal group size

  // Candidate break points: break point i (1-based, the group ends at element i) is allowed
  // only if elements i and i+1 differ, because items with the same value must share a group.
  vec<int> allowed;
  for (int i = 1; i < N; ++i)
    if (a[i - 1] != a[i]) allowed.push(i);
  int m = allowed.size();

  // pick[j] chooses the j-th break point among the allowed ones; x[j] is the 1-based
  // index of the last element of group j (the break point)
  vec<IntVar*> pick, x;
  createVars(pick, k - 1, 0, m - 1, true);
  for (int j = 0; j < k - 1; ++j) {
    x.push(newIntVar(1, N - 1));
    array_int_element(pick[j], allowed, x[j]);
  }

  // break points are increasing
  for (int j = 0; j + 1 < k - 1; ++j) int_rel(pick[j], IRT_LT, pick[j + 1]);

  // error of a group = abs(size - round(N/k)); the total error is minimized
  vec<IntVar*> errors;
  for (int j = 0; j < k; ++j) {
    // size of group j = its break point - the previous break point (0 and N are the outer limits)
    IntVar* hi = (j < k - 1) ? x[j] : getConstant(N);
    IntVar* lo = (j > 0) ? x[j - 1] : getConstant(0);
    IntVar* size = newIntVar(1, N);
    int_minus(hi, lo, size);
    IntVar* diff = newIntVar(-N, N);
    int_rel(size, IRT_EQ, diff, target);  // size = diff + target
    IntVar* err = newIntVar(0, N);
    int_abs(diff, err);
    errors.push(err);
  }
  IntVar* total_error = newIntVar(0, k * N);
  int_linear(errors, IRT_EQ, total_error);

  // search: try the smallest total error first (increasing it only when that fails), then the break points
  vec<IntVar*> objective_first;
  objective_first.push(total_error);
  branch(objective_first, VAR_INORDER, VAL_MIN);
  branch(pick, VAR_INORDER, VAL_MIN);
  optimize(total_error, OPT_MIN);

  json out = json::array();
  for (int j = 0; j < k - 1; ++j) out.push_back(dcp::out(x[j]));
  outputs = {{"x", out}};
}
