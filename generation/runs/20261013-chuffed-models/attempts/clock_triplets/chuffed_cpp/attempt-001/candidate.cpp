// Clock triplets: arrange the numbers 1 to 12 on a clock face so that no three adjacent numbers
// have a sum above 21.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // x[i] is the number at position i on the clock face (positions go round the circle)
  vec<IntVar*> x;
  createVars(x, 12, 1, 12, true);

  // every number from 1 to 12 appears exactly once
  all_different(x);

  // every three adjacent positions, wrapping round the face, have a sum of at most 21
  // (21 is the bound from the problem statement)
  for (int i = 0; i < 12; ++i) {
    vec<IntVar*> triple;
    triple.push(x[i]);
    triple.push(x[(i + 1) % 12]);
    triple.push(x[(i + 2) % 12]);
    int_linear(triple, IRT_LE, 21);
  }

  // place the numbers in order around the face
  branch(x, VAR_INORDER, VAL_MIN);

  json arr = json::array();
  for (int i = 0; i < 12; ++i) arr.push_back(dcp::out(x[i]));
  outputs = {{"x", arr}};
}
