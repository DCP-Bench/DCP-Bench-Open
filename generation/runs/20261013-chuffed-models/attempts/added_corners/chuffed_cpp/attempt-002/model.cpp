// Added corners: put the digits 1 to 8 in the eight positions of a ring so that each
// square equals the sum of the two circles next to it.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // positions[i] is the digit at position i, read left to right, top to bottom:
  //   C F C      positions 0 1 2   (circles at 0, 2, 5, 7; squares at 1, 3, 4, 6)
  //   F   F                3   4
  //   C F C                5 6 7
  vec<IntVar*> positions;
  createVars(positions, 8, 1, 8);

  // the digits 1 through 8 are each used once
  all_different(positions);

  // the number in each square equals the sum of the adjoining circles
  // square 1 = circle 0 + circle 2
  int_plus(positions[0], positions[2], positions[1]);
  // square 3 = circle 0 + circle 5
  int_plus(positions[0], positions[5], positions[3]);
  // square 4 = circle 2 + circle 7
  int_plus(positions[2], positions[7], positions[4]);
  // square 6 = circle 5 + circle 7
  int_plus(positions[5], positions[7], positions[6]);

  branch(positions, VAR_INORDER, VAL_MIN);

  json arr = json::array();
  for (int i = 0; i < 8; ++i) arr.push_back(dcp::out(positions[i]));
  outputs = {{"positions", arr}};
}
