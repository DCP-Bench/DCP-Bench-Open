// Among: exactly m entries of the array x take one of the values in v.
// All entries of x lie between 0 and 7, as the description states.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");
  int m = instance.at("m");
  std::vector<int> v = instance.at("v").get<std::vector<int>>();

  // x holds the n entries, each between 0 and 7
  vec<IntVar*> x;
  createVars(x, n, 0, 7);

  // inset[i] is 1 when x[i] takes one of the values in v
  vec<IntVar*> inset;
  for (int i = 0; i < n; ++i) {
    vec<BoolView> hits;
    for (int j = 0; j < (int)v.size(); ++j) {
      BoolView b = newBoolVar();
      int_rel_reif(x[i], IRT_EQ, v[j], b);
      hits.push(b);
    }
    IntVar* iv = newIntVar(0, 1);
    if (hits.size() == 0) {
      bool2int(bv_false, iv);
    } else {
      BoolView in = newBoolVar();
      array_bool_or(hits, in);
      bool2int(in, iv);
    }
    inset.push(iv);
  }

  // exactly m entries of x take one of the values in v
  int_linear(inset, IRT_EQ, m);

  branch(x, VAR_INORDER, VAL_MIN);
  json xs = json::array();
  for (int i = 0; i < n; ++i) xs.push_back(dcp::out(x[i]));
  outputs = {{"x", xs}};
}
