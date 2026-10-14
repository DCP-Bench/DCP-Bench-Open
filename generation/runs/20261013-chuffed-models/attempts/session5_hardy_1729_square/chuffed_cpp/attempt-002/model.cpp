// Hardy's 1729 square: find four different numbers between 1 and 100 such that
// a^2 + b^2 = c^2 + d^2.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // four different numbers between 1 and 100
  vec<IntVar*> x;
  createVars(x, 4, 1, 100);
  all_different(x);

  // the squares of the four numbers
  vec<IntVar*> sq;
  for (int i = 0; i < 4; ++i) {
    IntVar* s = newIntVar(1, 10000);
    int_times(x[i], x[i], s);
    sq.push(s);
  }

  // the sum of the squares of the two first numbers equals the sum of the squares of the other two
  vec<int> coef;
  coef.push(1);
  coef.push(1);
  coef.push(-1);
  coef.push(-1);
  int_linear(coef, sq, IRT_EQ, 0);

  branch(x, VAR_INORDER, VAL_MIN);
  outputs = {{"a", dcp::out(x[0])}, {"b", dcp::out(x[1])}, {"c", dcp::out(x[2])}, {"d", dcp::out(x[3])}};
}
