// Equal sized groups: split a sorted list into k groups by k-1 break points, keeping equal values together and group sizes close to round(N/k).
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> a = instance.at("a").get<std::vector<int>>();
  int k = instance.at("k");
  int N = static_cast<int>(a.size());
  int target = (2 * N + k) / (2 * k);  // round(N/k)

  // x[j] is the 1-based index of the last element of group j (the break point)
  vec<IntVar*> x;
  createVars(x, k - 1, 1, N - 1, true);

  // break points are increasing
  for (int j = 0; j + 1 < k - 1; ++j) int_rel(x[j], IRT_LT, x[j + 1]);

  // items with the same value must be in the same group: no break point between equal neighbours
  for (int i = 1; i < N; ++i)
    if (a[i - 1] == a[i])
      for (int j = 0; j < k - 1; ++j) int_rel(x[j], IRT_NE, i);

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

  branch(x, VAR_INORDER, VAL_SPLIT_MIN);
  optimize(total_error, OPT_MIN);

  json out = json::array();
  for (int j = 0; j < k - 1; ++j) out.push_back(dcp::out(x[j]));
  outputs = {{"x", out}};
}
