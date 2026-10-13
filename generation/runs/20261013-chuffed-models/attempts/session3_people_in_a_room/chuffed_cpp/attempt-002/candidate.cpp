// People in a room: 13 people, 4 of them male, enter one at a time; at every moment the
// ratio of females to males in the room must be at most 7/3.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  const int people = 13;  // problem constants from the statement
  const int males = 4;

  // sequence[k] = 1 if the k-th person to enter is female, 0 if male
  vec<IntVar*> sequence;
  createVars(sequence, people, 0, 1, true);

  // 4 of the 13 people are male, so 9 are female
  int_linear(sequence, IRT_EQ, people - males);

  // after k people have entered, females / males <= 7/3, that is 3 * females <= 7 * males
  // with males = k - females, i.e. 10 * females <= 7 * k (this also forces the first
  // person to be male, since a ratio with no male is unbounded)
  for (int k = 1; k <= people; ++k) {
    vec<int> co;
    vec<IntVar*> vs;
    for (int i = 0; i < k; ++i) { co.push(10); vs.push(sequence[i]); }
    int_linear(co, vs, IRT_LE, 7 * k);
  }

  branch(sequence, VAR_INORDER, VAL_MIN);

  json arr = json::array();
  for (int i = 0; i < people; ++i) arr.push_back(dcp::out(sequence[i]));
  outputs = {{"sequence", arr}};
}
