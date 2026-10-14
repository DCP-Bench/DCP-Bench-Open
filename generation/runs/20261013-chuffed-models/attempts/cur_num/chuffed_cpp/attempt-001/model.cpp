// Curious number: find a number x between 1 and 10000, other than 48, such that x + 1 is a square
// and x / 2 + 1 is also a square. (48 is the example: 49 = 7*7 and 24 + 1 = 25 = 5*5.)
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // x is the curious number, 1 to 10000 (the problem's range)
  IntVar* x = newIntVar(1, 10000);

  // 48 is the example in the problem statement, so it is excluded
  int_rel(x, IRT_NE, 48);

  // x + 1 is a square: x + 1 = s * s
  IntVar* s = newIntVar(1, 101);
  IntVar* s_sq = newIntVar(1, 101 * 101);
  int_times(s, s, s_sq);
  vec<int> c1;
  c1.push(1);
  c1.push(-1);
  vec<IntVar*> v1;
  v1.push(x);
  v1.push(s_sq);
  int_linear(c1, v1, IRT_EQ, -1);

  // x / 2 + 1 is a square: x = 2 * (t * t - 1), so x - 2 * (t * t) = -2 with x even
  IntVar* t = newIntVar(1, 71);
  IntVar* t_sq = newIntVar(1, 71 * 71);
  int_times(t, t, t_sq);
  vec<int> c2;
  c2.push(1);
  c2.push(-2);
  vec<IntVar*> v2;
  v2.push(x);
  v2.push(t_sq);
  int_linear(c2, v2, IRT_EQ, -2);

  // the squares are the decision variables
  vec<IntVar*> search;
  search.push(x);
  search.push(s);
  search.push(t);
  branch(search, VAR_INORDER, VAL_MIN);

  outputs = {{"peculiar", dcp::out(x)}};
}
