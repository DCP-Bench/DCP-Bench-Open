// Broken weights: a weight of m pounds broke into n pieces of whole-pound weights that can
// still weigh every whole number of pounds from 1 to m on a balance scale.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int m = instance.at("m");
  int n = instance.at("n");

  // weights[i] is the weight in pounds of piece i (at least one pound)
  vec<IntVar*> weights;
  createVars(weights, n, 1, m);

  // the pieces together weigh the whole m pounds
  vec<int> ones;
  for (int i = 0; i < n; ++i) ones.push(1);
  int_linear(ones, weights, IRT_EQ, m);

  // the pieces have different weights, listed in increasing order (the reference's all-different rule;
  // the order only removes permutations of the same set of pieces)
  for (int i = 0; i + 1 < n; ++i) int_rel(weights[i], IRT_LT, weights[i + 1]);

  // for every weight t from 1 to m, the pieces can be placed so that t is balanced:
  // side[i] = +1 puts piece i on the object's pan, -1 on the opposite pan, 0 leaves it off the scale
  vec<IntVar*> all_sides;
  for (int t = 1; t <= m; ++t) {
    vec<IntVar*> side;
    createVars(side, n, -1, 1, true);

    // the signed weights of the pieces on the scale add up to t
    vec<IntVar*> signed_w;
    for (int i = 0; i < n; ++i) {
      IntVar* sw = newIntVar(-m, m);
      int_times(weights[i], side[i], sw);
      signed_w.push(sw);
    }
    vec<int> ones2;
    for (int i = 0; i < n; ++i) ones2.push(1);
    int_linear(ones2, signed_w, IRT_EQ, t);

    for (int i = 0; i < n; ++i) all_sides.push(side[i]);
  }

  // decide the piece weights first, then the placements
  branch(weights, VAR_INORDER, VAL_MIN);
  branch(all_sides, VAR_INORDER, VAL_MIN);

  json ws = json::array();
  for (int i = 0; i < n; ++i) ws.push_back(dcp::out(weights[i]));
  outputs = {{"weights", ws}};
}
