// Frog circle: arrange the cards 1 to n in a circle so that a frog, starting on card 1 and jumping
// from card k over k cards clockwise each time, lands on every card.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");

  // x[p] is the card at position p of the circle (positions 0 .. n-1, clockwise)
  vec<IntVar*> x;
  createVars(x, n, 1, n);

  // every card 1 to n is on the circle exactly once
  all_different(x);

  // the circle can be turned freely, so card 1 is fixed at position 0 (the reference counts
  // arrangements with this convention); the frog starts there
  int_rel(x[0], IRT_EQ, 1);

  // pos[t] is the position of the frog after t jumps; pos[0] = 0 is the start on card 1
  vec<IntVar*> pos;
  createVars(pos, n, 0, n - 1);
  int_rel(pos[0], IRT_EQ, 0);

  // the frog jumps from position p over the card value x[p] clockwise: next = (p + x[p]) mod n.
  // Written as pos[t] + card = pos[t+1] + n * wrap, with wrap in 0..1.
  for (int t = 0; t + 1 < n; ++t) {
    // card is the card the frog stands on after t jumps
    IntVar* card = newIntVar(1, n);
    array_var_int_element_bound(pos[t], x, card);

    // wrap is 1 when the jump goes past the last position of the circle
    IntVar* wrap = newIntVar(0, 1);
    vec<int> coef;
    coef.push(1);
    coef.push(1);
    coef.push(-1);
    coef.push(-n);
    vec<IntVar*> terms;
    terms.push(pos[t]);
    terms.push(card);
    terms.push(pos[t + 1]);
    terms.push(wrap);
    int_linear(coef, terms, IRT_EQ, 0);
  }

  // the frog must land on every card, so its positions are all different
  all_different(pos);

  // decide the arrangement first
  branch(x, VAR_INORDER, VAL_MIN);
  branch(pos, VAR_INORDER, VAL_MIN);

  json arr = json::array();
  for (int p = 0; p < n; ++p) arr.push_back(dcp::out(x[p]));
  outputs = {{"x", arr}};
}
