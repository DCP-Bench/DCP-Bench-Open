// Magic sequence: find x_0 .. x_{n-1}, each between 0 and n-1, such that the number i occurs
// exactly x_i times in the sequence, for every i.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");

  // x[i] is the i-th element of the sequence, a value from 0 to n-1
  vec<IntVar*> x;
  createVars(x, n, 0, n - 1, true);

  // the sequence has n elements in total, so the counts add up to n
  vec<int> ones;
  for (int i = 0; i < n; ++i) ones.push(1);
  int_linear(ones, x, IRT_EQ, n);

  // for every value i, the number of positions j with x_j = i must equal x_i
  for (int i = 0; i < n; ++i) {
    // hit[j] is true exactly when the element at position j equals i
    vec<BoolView> hit;
    for (int j = 0; j < n; ++j) {
      BoolView b = newBoolVar();
      int_rel_reif(x[j], IRT_EQ, i, b);
      hit.push(b);
    }

    // the number of hits for value i is x_i
    bool_linear(hit, IRT_EQ, x[i]);
  }

  // decide the sequence in order
  branch(x, VAR_INORDER, VAL_MIN);

  json arr = json::array();
  for (int i = 0; i < n; ++i) arr.push_back(dcp::out(x[i]));
  outputs = {{"x", arr}};
}
