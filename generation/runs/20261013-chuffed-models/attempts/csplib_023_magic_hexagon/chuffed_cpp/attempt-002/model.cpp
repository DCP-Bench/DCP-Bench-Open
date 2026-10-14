// Magic hexagon: place the numbers 1 to 19 on the 19 cells of a hexagon so that
// each of the 15 lines sums to the magic constant.
#include "dcp.h"

#include <vector>

// post one line: the cells at the given indices sum to magic
static void magic_line(vec<IntVar*>& cells, const std::vector<int>& idx, int magic) {
  vec<IntVar*> t;
  for (int i : idx) t.push(cells[i]);
  int_linear(t, IRT_EQ, magic);
}

void Build(const json& instance, json& outputs) {
  int n = instance.at("NUM_CELLS");
  int magic = instance.at("MAGIC_SUM");

  // LD[i] is the number in cell i, cells in order A, B, ..., S
  // (A=0 B=1 C=2 D=3 E=4 F=5 G=6 H=7 I=8 J=9 K=10 L=11 M=12 N=13 O=14 P=15 Q=16 R=17 S=18)
  vec<IntVar*> ld;
  createVars(ld, n, 1, n);

  // the numbers 1 to 19 each appear once
  all_different(ld);

  // the rows of the hexagon: ABC, DEFG, HIJKL, MNOP, QRS
  magic_line(ld, {0, 1, 2}, magic);
  magic_line(ld, {3, 4, 5, 6}, magic);
  magic_line(ld, {7, 8, 9, 10, 11}, magic);
  magic_line(ld, {12, 13, 14, 15}, magic);
  magic_line(ld, {16, 17, 18}, magic);

  // the down-right diagonals: AEJOS, BFKP, CGL, DINR, HMQ
  magic_line(ld, {0, 4, 9, 14, 18}, magic);
  magic_line(ld, {1, 5, 10, 15}, magic);
  magic_line(ld, {2, 6, 11}, magic);
  magic_line(ld, {3, 8, 13, 17}, magic);
  magic_line(ld, {7, 12, 16}, magic);

  // the down-left diagonals: CFJNQ, BEIM, ADH, GKOR, LPS
  magic_line(ld, {2, 5, 9, 13, 16}, magic);
  magic_line(ld, {1, 4, 8, 12}, magic);
  magic_line(ld, {0, 3, 7}, magic);
  magic_line(ld, {6, 10, 14, 17}, magic);
  magic_line(ld, {11, 15, 18}, magic);

  // branch on the cells in order, trying the smallest value first
  branch(ld, VAR_INORDER, VAL_MIN);

  json arr = json::array();
  for (int i = 0; i < n; ++i) arr.push_back(dcp::out(ld[i]));
  outputs = {{"LD", arr}};
}
