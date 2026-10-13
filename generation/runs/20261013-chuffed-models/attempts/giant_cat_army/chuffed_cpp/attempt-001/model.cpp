// Giant cat army: build a list from 0 by adding 5, adding 7 or taking the square root of
// the last element, with all elements distinct integers <= 60, containing 2, 10 and 14
// in that order, of length 24, ending with 14.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // the list length and the bound on its elements are problem constants from the description
  const int len = 24;
  const int max_value = 60;

  // x[t] is the element at position t of the list
  vec<IntVar*> x;
  createVars(x, len, 0, max_value);

  // the list starts with 0
  int_rel(x[0], IRT_EQ, 0);

  // the list ends with 14
  int_rel(x[len - 1], IRT_EQ, 14);

  // all the elements are distinct
  all_different(x);

  // each step applies exactly one operation: add 5, add 7 or take the square root
  for (int t = 0; t + 1 < len; ++t) {
    BoolView add5 = newBoolVar();
    BoolView add7 = newBoolVar();
    BoolView root = newBoolVar();
    vec<BoolView> ops;
    ops.push(add5);
    ops.push(add7);
    ops.push(root);
    bool_linear(ops, IRT_EQ, getConstant(1));

    // add 5: the next element is the current one plus 5
    int_rel_half_reif(x[t + 1], IRT_EQ, x[t], add5, 5);

    // add 7: the next element is the current one plus 7
    int_rel_half_reif(x[t + 1], IRT_EQ, x[t], add7, 7);

    // take the square root: the next element squared is the current element
    IntVar* sq = newIntVar(0, max_value * max_value);
    int_times(x[t + 1], x[t + 1], sq);
    int_rel_half_reif(sq, IRT_EQ, x[t], root);
  }

  // 2 appears in the list, 10 appears in the list, and 2 comes before 10
  vec<BoolView> has2, has10;
  vec<IntVar*> at2, at10;
  vec<int> position;
  for (int i = 0; i < len; ++i) {
    BoolView b2 = newBoolVar();
    int_rel_reif(x[i], IRT_EQ, 2, b2);
    has2.push(b2);
    IntVar* i2 = newIntVar(0, 1);
    bool2int(b2, i2);
    at2.push(i2);

    BoolView b10 = newBoolVar();
    int_rel_reif(x[i], IRT_EQ, 10, b10);
    has10.push(b10);
    IntVar* i10 = newIntVar(0, 1);
    bool2int(b10, i10);
    at10.push(i10);

    position.push(i);
  }
  bool_clause(has2);
  bool_clause(has10);

  // pos2 is the position of the 2 and pos10 the position of the 10
  IntVar* pos2 = newIntVar(0, len - 1);
  int_linear(position, at2, IRT_EQ, pos2);
  IntVar* pos10 = newIntVar(0, len - 1);
  int_linear(position, at10, IRT_EQ, pos10);

  // the 2 comes before the 10, and the 10 comes before the final 14
  int_rel(pos2, IRT_LT, pos10);
  int_rel(pos10, IRT_LT, len - 1);

  // branch on the list in order, smallest value first
  branch(x, VAR_INORDER, VAL_MIN);

  json arr = json::array();
  for (int i = 0; i < len; ++i) arr.push_back(dcp::out(x[i]));
  outputs = {{"x", arr}};
}
