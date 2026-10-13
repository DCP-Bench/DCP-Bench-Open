// Magic hexagon: place the numbers 1 to 19 in the cells of a hexagon of side 3 so that
// every one of its 15 lines (five lines in each of three directions) sums to 38.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // cells A..S in reading order; the hexagon has 19 cells holding the numbers 1..19
  vec<IntVar*> cell;
  createVars(cell, 19, 1, 19);

  // the 19 numbers are all different
  all_different(cell);

  // index of each letter: A=0 B=1 C=2 D=3 E=4 F=5 G=6 H=7 I=8 J=9 K=10 L=11 M=12 N=13 O=14 P=15 Q=16 R=17 S=18
  // the 15 lines of the hexagon, as lists of cell indices
  int lines[15][5] = {
      // the three horizontal rows (widths 3, 4, 5, 4, 3)
      {0, 1, 2, -1, -1}, {3, 4, 5, 6, -1}, {7, 8, 9, 10, 11}, {12, 13, 14, 15, -1}, {16, 17, 18, -1, -1},
      // the lines running down to the right
      {7, 12, 16, -1, -1}, {3, 8, 13, 17, -1}, {0, 4, 9, 14, 18}, {1, 5, 10, 15, -1}, {2, 6, 11, -1, -1},
      // the lines running down to the left
      {0, 3, 7, -1, -1}, {1, 4, 8, 12, -1}, {2, 5, 9, 13, 16}, {6, 10, 14, 17, -1}, {11, 15, 18, -1, -1}};
  int lens[15] = {3, 4, 5, 4, 3, 3, 4, 5, 4, 3, 3, 4, 5, 4, 3};

  // every line sums to the magic constant 38 (the sum of 1..19 divided by 5 rows)
  const int magic = 38;
  for (int l = 0; l < 15; ++l) {
    vec<IntVar*> line;
    vec<int> ones;
    for (int k = 0; k < lens[l]; ++k) {
      line.push(cell[lines[l][k]]);
      ones.push(1);
    }
    int_linear(ones, line, IRT_EQ, magic);
  }

  // the search goes through the cells in reading order
  branch(cell, VAR_INORDER, VAL_MIN);

  json ld = json::array();
  for (int i = 0; i < 19; ++i) ld.push_back(dcp::out(cell[i]));
  outputs = {{"LD", ld}};
}
