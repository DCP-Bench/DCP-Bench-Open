// Schur's lemma: put n balls into c boxes so that no triple x + y = z lies in a single box.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");
  int c = instance.at("c");  // number of boxes

  // balls[i-1] is the box (1..c) of ball i; M[i-1][j-1] is true if ball i is in box j
  vec<IntVar*> balls;
  createVars(balls, n, 1, c, true);
  vec<vec<BoolView>> M;
  createVars(M, n, c);

  // a ball must be in exactly one box
  for (int i = 0; i < n; ++i)
    for (int j = 1; j <= c; ++j) int_rel_reif(balls[i], IRT_EQ, j, M[i][j - 1]);

  // for each x + y = z and each box j: not (M[x][j] and M[y][j] and M[z][j])
  for (int x = 1; x <= n; ++x)
    for (int y = x; x + y <= n; ++y) {  // y = x is allowed: the triple is (x, x, 2x)
      int z = x + y;
      for (int j = 0; j < c; ++j) {
        vec<BoolView> pos, neg;
        neg.push(M[x - 1][j]);
        neg.push(M[y - 1][j]);
        neg.push(M[z - 1][j]);
        bool_clause(pos, neg);
      }
    }

  branch(balls, VAR_INORDER, VAL_MIN);
  json out = json::array();
  for (int i = 0; i < n; ++i) out.push_back(dcp::out(balls[i]));
  outputs = {{"balls", out}};
}
