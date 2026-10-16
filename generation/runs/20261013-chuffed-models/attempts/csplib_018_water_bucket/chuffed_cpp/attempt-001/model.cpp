// Water buckets (CSPLib 18): three buckets with capacities 8, 5 and 3 pints start with 8, 0, 0.
// Find the fewest pours between buckets that leave 4 pints in the 8-pint bucket and 4 pints
// in the 5-pint bucket. sequence[t] is the state of the buckets after t pours (sequence[0] is
// the start). After the goal is reached the remaining steps hold the padding state.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> cap = instance.at("capacities").get<std::vector<int>>();
  std::vector<int> init = instance.at("initial_state").get<std::vector<int>>();
  std::vector<int> goal = instance.at("goal_state").get<std::vector<int>>();
  int steps = instance.at("MAX_STEPS");
  int pad = instance.at("PADDING_VALUE");
  int total = init[0] + init[1] + init[2];

  // state[3*t+k] is the water in bucket k after t pours; a padded step holds the padding value
  vec<IntVar*> state;
  for (int t = 0; t < steps; ++t) {
    for (int k = 0; k < 3; ++k) {
      int lo = pad < 0 ? pad : 0;
      state.push(newIntVar(lo, cap[k]));
    }
  }

  // the start state is the initial one
  for (int k = 0; k < 3; ++k) int_rel(state[k], IRT_EQ, init[k]);

  // legal transitions as tuples (from-state, to-state), each six numbers
  // a pour moves water from bucket i to bucket j until i is empty or j is full
  vec<vec<int>> moves;
  for (int a = 0; a <= cap[0]; ++a) {
    for (int b = 0; b <= cap[1]; ++b) {
      for (int c = 0; c <= cap[2]; ++c) {
        if (a + b + c != total) continue;  // water is conserved
        int from[3] = {a, b, c};
        for (int i = 0; i < 3; ++i) {
          for (int j = 0; j < 3; ++j) {
            if (i == j) continue;
            int amount = from[i] < cap[j] - from[j] ? from[i] : cap[j] - from[j];
            if (amount <= 0) continue;
            int to[3] = {a, b, c};
            to[i] -= amount;
            to[j] += amount;
            moves.push();
            for (int k = 0; k < 3; ++k) moves.last().push(from[k]);
            for (int k = 0; k < 3; ++k) moves.last().push(to[k]);
          }
        }
      }
    }
  }
  // once the goal is reached the sequence is padded: padding stays padding,
  // and the goal may be followed by padding
  moves.push();
  for (int k = 0; k < 6; ++k) moves.last().push(pad);
  moves.push();
  for (int k = 0; k < 3; ++k) moves.last().push(goal[k]);
  for (int k = 0; k < 3; ++k) moves.last().push(pad);

  // every step is a pour (or padding) from the step before
  for (int t = 0; t + 1 < steps; ++t) {
    vec<IntVar*> pair;
    for (int k = 0; k < 3; ++k) pair.push(state[3 * t + k]);
    for (int k = 0; k < 3; ++k) pair.push(state[3 * (t + 1) + k]);
    table(pair, moves);
  }

  // the last step is either the goal or padding, so the goal is reached within the steps
  vec<vec<int>> ends;
  ends.push();
  for (int k = 0; k < 3; ++k) ends.last().push(goal[k]);
  ends.push();
  for (int k = 0; k < 3; ++k) ends.last().push(pad);
  vec<IntVar*> last;
  for (int k = 0; k < 3; ++k) last.push(state[3 * (steps - 1) + k]);
  table(last, ends);

  // pads[t] is true when step t is padding, for the steps after the start
  vec<BoolView> pads;
  for (int t = 1; t < steps; ++t) {
    BoolView p = newBoolVar();
    int_rel_reif(state[3 * t], IRT_EQ, pad, p);
    pads.push(p);
  }

  // the number of pours is the number of real steps after the start, that is the steps
  // minus the padded ones minus one: cost + padded = steps - 1
  IntVar* padded = newIntVar(0, steps - 1);
  bool_linear(pads, IRT_EQ, padded);
  IntVar* cost = newIntVar(0, steps - 1);
  vec<int> coef;
  coef.push(1);
  coef.push(1);
  vec<IntVar*> cp;
  cp.push(cost);
  cp.push(padded);
  int_linear(coef, cp, IRT_EQ, steps - 1);

  // the start state of each bucket and the step states are the decision variables
  branch(state, VAR_INORDER, VAL_MIN);

  // minimise the number of pours
  optimize(cost, OPT_MIN);

  json seq = json::array();
  for (int t = 0; t < steps; ++t) {
    json st = json::array();
    for (int k = 0; k < 3; ++k) st.push_back(dcp::out(state[3 * t + k]));
    seq.push_back(st);
  }
  outputs = {{"cost", dcp::out(cost)}, {"sequence", seq}};
}
