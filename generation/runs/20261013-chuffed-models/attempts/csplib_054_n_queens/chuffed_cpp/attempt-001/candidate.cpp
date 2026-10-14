// N-queens: place n queens on an n x n board so that no two attack each other.
// queens[i] is the column (1 to n) of the queen in row i+1.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");

  vec<IntVar*> queens;
  createVars(queens, n, 1, n);

  // no two queens share a column
  all_different(queens);

  // no two queens share a diagonal: queens[i] + i and queens[i] - i are all different
  vec<int> up, down;
  for (int i = 0; i < n; ++i) {
    up.push(i);
    down.push(-i);
  }
  all_different_offset(up, queens);
  all_different_offset(down, queens);

  // the queens are the decision variables; place them row by row
  branch(queens, VAR_INORDER, VAL_MIN);

  json cols = json::array();
  for (int i = 0; i < n; ++i) cols.push_back(dcp::out(queens[i]));
  outputs = {{"queens", cols}};
}
