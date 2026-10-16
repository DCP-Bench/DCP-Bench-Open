// Guards and apples: a boy bribes each guard with half of his apples plus one, in whole
// apples, and has exactly the one apple for the girl after the last gate.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int num_gates = instance.at("num_gates");

  // apples[i] is the number of apples before gate i; apples[num_gates] is the number left
  // after the last gate. The bound is generous; the values are fixed by the constraints.
  vec<IntVar*> apples;
  createVars(apples, num_gates + 1, 0, 100000000);

  // he gives the girl one apple after the last gate and has no apples left afterwards
  int_rel(apples[num_gates], IRT_EQ, 1);

  // he bribes each guard with half of his apples plus one, an integer number of apples
  // (no knife, so the number he holds before each gate is even)
  for (int i = 0; i < num_gates; ++i) {
    IntVar* half = newIntVar(0, 50000000);  // half of the apples before gate i
    vec<int> two_h;                          // apples[i] = 2 * half
    vec<IntVar*> hv;
    hv.push(half);
    two_h.push(2);
    int_linear(two_h, hv, IRT_EQ, apples[i]);
    // apples after the gate = apples before - (half + 1)
    vec<int> co;
    vec<IntVar*> vs;
    co.push(1); vs.push(apples[i]);
    co.push(-1); vs.push(half);
    co.push(-1); vs.push(apples[i + 1]);
    int_linear(co, vs, IRT_EQ, 1);
  }

  branch(apples, VAR_INORDER, VAL_MIN);

  json arr = json::array();
  for (int i = 0; i <= num_gates; ++i) arr.push_back(dcp::out(apples[i]));
  outputs = {{"apples", arr}};
}
