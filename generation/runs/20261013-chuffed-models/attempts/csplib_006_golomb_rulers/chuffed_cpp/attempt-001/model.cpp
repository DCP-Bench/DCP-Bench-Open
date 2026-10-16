// Golomb ruler: place m marks at integer positions, starting at 0, so that all pairwise differences are distinct and the ruler is as short as possible.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int m = instance.at("size");

  // upper bound on the length of an optimal ruler with m marks: m*m is safe for the sizes in use
  // (known optimal lengths are well below m^2)
  int max_length = m * m;

  // marks[i] is the position of the i-th mark
  vec<IntVar*> marks;
  createVars(marks, m, 0, max_length);

  // the first mark is at position 0
  int_rel(marks[0], IRT_EQ, 0);

  // the marks are strictly increasing: a_1 < a_2 < ... < a_m
  for (int i = 0; i + 1 < m; ++i) {
    int_rel(marks[i + 1], IRT_GT, marks[i]);
  }

  // the m(m-1)/2 differences a_j - a_i (i < j) are distinct
  vec<IntVar*> diffs;
  for (int i = 0; i < m; ++i) {
    for (int j = i + 1; j < m; ++j) {
      IntVar* d = newIntVar(1, max_length);
      int_minus(marks[j], marks[i], d);
      diffs.push(d);
    }
  }
  all_different(diffs);

  // the length of the ruler is the position of the last mark; minimize it
  IntVar* length = marks[m - 1];
  branch(marks, VAR_INORDER, VAL_MIN);
  optimize(length, OPT_MIN);

  json pos = json::array();
  for (int i = 0; i < m; ++i) pos.push_back(dcp::out(marks[i]));
  outputs = {{"marks", pos}, {"length", dcp::out(length)}};
}
