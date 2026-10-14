// Bin packing: assign each item to a bin so that the total weight in each bin does not exceed the capacity.
#include "dcp.h"
#include <algorithm>
#include <numeric>

void Build(const json& instance, json& outputs) {
  std::vector<int> weights = instance.at("weights").get<std::vector<int>>();
  int capacity = instance.at("capacity");
  int num_bins = instance.at("num_bins");
  int n = static_cast<int>(weights.size());

  // bins[i] is the bin (0-indexed) item i is assigned to
  vec<IntVar*> bins;
  createVars(bins, n, 0, num_bins - 1, true);

  // in_bin[i][b] = 1 exactly when item i is in bin b
  vec<vec<IntVar*>> in_bin;
  createVars(in_bin, n, num_bins, 0, 1, true);
  for (int i = 0; i < n; ++i)
    for (int b = 0; b < num_bins; ++b) {
      BoolView r = newBoolVar();
      int_rel_reif(bins[i], IRT_EQ, b, r);
      bool2int(r, in_bin[i][b]);
    }

  // the total weight of the items in each bin does not exceed the capacity
  for (int b = 0; b < num_bins; ++b) {
    vec<int> w;
    vec<IntVar*> col;
    for (int i = 0; i < n; ++i) {
      w.push(weights[i]);
      col.push(in_bin[i][b]);
    }
    int_linear(w, col, IRT_LE, capacity);
  }

  // place heavy items first: they are the hardest to fit
  std::vector<int> order(n);
  std::iota(order.begin(), order.end(), 0);
  std::stable_sort(order.begin(), order.end(), [&](int a, int b) { return weights[a] > weights[b]; });
  vec<IntVar*> by_weight;
  for (int i : order) by_weight.push(bins[i]);
  branch(by_weight, VAR_INORDER, VAL_MIN);

  json out = json::array();
  for (int i = 0; i < n; ++i) out.push_back(dcp::out(bins[i]));
  outputs = {{"bins", out}};
}
