// Climb a stair of n steps taking between m1 and m2 steps per move; unused moves are 0.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");
  int m1 = instance.at("m1");
  int m2 = instance.at("m2");

  // steps[i] is the number of steps taken at move i, or 0 once the top has been reached
  vec<IntVar*> steps;
  createVars(steps, n, 0, m2, true);

  // each move takes between m1 and m2 steps (or 0 if no steps are taken)
  for (int i = 0; i < n; ++i)
    for (int v = 1; v < m1; ++v) int_rel(steps[i], IRT_NE, v);

  // the moves together climb exactly the n steps of the stair
  int_linear(steps, IRT_EQ, n);

  // after we reach the top of the stair no more steps are taken: a 0 move is followed by 0 moves
  vec<BoolView> none;
  createVars(none, n);
  for (int i = 0; i < n; ++i) int_rel_reif(steps[i], IRT_EQ, 0, none[i]);
  for (int i = 0; i + 1 < n; ++i) {
    vec<BoolView> pos, neg;
    pos.push(none[i + 1]);
    neg.push(none[i]);
    bool_clause(pos, neg);
  }

  branch(steps, VAR_INORDER, VAL_MAX);
  json arr = json::array();
  for (int i = 0; i < n; ++i) arr.push_back(dcp::out(steps[i]));
  outputs = {{"steps", arr}};
}
