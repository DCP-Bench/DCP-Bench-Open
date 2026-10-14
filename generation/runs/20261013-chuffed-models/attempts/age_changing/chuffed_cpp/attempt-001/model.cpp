// Age changing: applying +2, /8, -3, *7 in some order to my age gives my husband's age,
// and applying the same four operations in a different order to his age gives mine.
#include "dcp.h"

// Adds the chain "start, then the four operations in some order, ends at finish" and returns the order variables.
// order[t] is the operation applied at step t: 0 is +2, 1 is /8, 2 is -3, 3 is *7.
static void PostChain(IntVar* start, IntVar* finish, vec<IntVar*>& order) {
  // The value ranges below are my own bounds: ages are at most 150, and intermediate values stay
  // within -30..1100 (the largest is (150 + 2) * 7).
  const int max_age = 150, lo = -30, hi = 1100;
  vec<vec<int>> steps;  // (operation, value before, value after) for every allowed application
  for (int v = lo; v <= hi; ++v) {
    int after[4] = {v + 2, v % 8 == 0 ? v / 8 : lo - 1, v - 3, v * 7};  // division only when exact
    for (int op = 0; op < 4; ++op) {
      if (after[op] < lo || after[op] > hi) continue;
      steps.push();
      steps.last().push(op);
      steps.last().push(v);
      steps.last().push(after[op]);
    }
  }
  (void)max_age;

  // value[t] is the number after t operations
  vec<IntVar*> value;
  value.push(start);
  for (int t = 1; t < 4; ++t) value.push(newIntVar(lo, hi));
  value.push(finish);

  // each of the four operations is applied exactly once
  createVars(order, 4, 0, 3, true);
  all_different(order);

  // each step applies the chosen operation to the current number
  for (int t = 0; t < 4; ++t) {
    vec<IntVar*> tup;
    tup.push(order[t]);
    tup.push(value[t]);
    tup.push(value[t + 1]);
    table(tup, steps);
  }
}

void Build(const json& instance, json& outputs) {
  const int max_age = 150;  // my own bound on a plausible age

  // m is my age and h is my husband's age (positive years)
  IntVar* m = newIntVar(1, max_age);
  IntVar* h = newIntVar(1, max_age);

  // starting with my age and applying the four operations in some order gives my husband's age
  vec<IntVar*> order_m;
  PostChain(m, h, order_m);

  // starting with his age and applying the same operations in a different order gives my age
  vec<IntVar*> order_h;
  PostChain(h, m, order_h);
  vec<IntVar*> differ_a, differ_b;
  for (int t = 0; t < 4; ++t) {
    differ_a.push(order_m[t]);
    differ_b.push(order_h[t]);
  }
  // the second order is different from the first: they are not the same sequence
  vec<BoolView> same;
  createVars(same, 4);
  for (int t = 0; t < 4; ++t) int_rel_reif(order_m[t], IRT_EQ, order_h[t], same[t]);
  vec<BoolView> neg, pos;
  for (int t = 0; t < 4; ++t) neg.push(same[t]);
  bool_clause(pos, neg);

  vec<IntVar*> ages;
  ages.push(m);
  ages.push(h);
  branch(ages, VAR_INORDER, VAL_MIN);
  outputs = {{"h", dcp::out(h)}, {"m", dcp::out(m)}};
}
