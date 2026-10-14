// Hadamard matrix (Legendre pairs): +-1 sequences a, b of length l with prescribed periodic autocorrelations.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int l = instance.at("l");
  int m = (l - 1) / 2;

  // a[i], b[i] take values -1 or +1
  vec<IntVar*> a, b;
  createVars(a, l, -1, 1, true);
  createVars(b, l, -1, 1, true);
  for (int i = 0; i < l; ++i) {
    int_rel(a[i], IRT_NE, 0);
    int_rel(b[i], IRT_NE, 0);
  }

  // PAF(A, s) + PAF(B, s) = -2 for s = 1..m, with indices taken modulo l
  for (int s = 1; s <= m; ++s) {
    vec<IntVar*> products;
    for (int i = 0; i < l; ++i) {
      IntVar* pa = newIntVar(-1, 1);
      int_times(a[i], a[(i + s) % l], pa);
      products.push(pa);
      IntVar* pb = newIntVar(-1, 1);
      int_times(b[i], b[(i + s) % l], pb);
      products.push(pb);
    }
    int_linear(products, IRT_EQ, -2);
  }

  // a_1 + ... + a_l = 1 and b_1 + ... + b_l = 1
  int_linear(a, IRT_EQ, 1);
  int_linear(b, IRT_EQ, 1);

  vec<IntVar*> all;
  for (int i = 0; i < l; ++i) all.push(a[i]);
  for (int i = 0; i < l; ++i) all.push(b[i]);
  branch(all, VAR_INORDER, VAL_MIN);

  json ja = json::array(), jb = json::array();
  for (int i = 0; i < l; ++i) ja.push_back(dcp::out(a[i]));
  for (int i = 0; i < l; ++i) jb.push_back(dcp::out(b[i]));
  outputs = {{"a", ja}, {"b", jb}};
}
