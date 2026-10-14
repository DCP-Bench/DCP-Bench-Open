// Generate an 18-hole golf course: each hole has length 3, 4 or 5 and the total length is 72.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // The numbers of holes (18), the allowed lengths (3..5) and the total (72) are fixed by the problem statement.
  const int num_holes = 18, shortest = 3, longest = 5, total_length = 72;

  // holes[i] is the length of hole i
  vec<IntVar*> holes;
  createVars(holes, num_holes, shortest, longest);

  // the total length of the course is 72
  int_linear(holes, IRT_EQ, total_length);

  branch(holes, VAR_INORDER, VAL_MIN);
  json arr = json::array();
  for (int i = 0; i < num_holes; ++i) arr.push_back(dcp::out(holes[i]));
  outputs = {{"holes", arr}};
}
