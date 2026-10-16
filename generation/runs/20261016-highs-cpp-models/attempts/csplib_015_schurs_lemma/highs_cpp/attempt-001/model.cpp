// CSPLib 015, Schur's lemma: put the balls 1..n into boxes so that for any triple of balls
// (x, y, z) with x + y = z, not all three are in the same box. The number of boxes is c
// (an instance field; the description fixes it at 3).
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n").get<int>();
  int c = instance.at("c").get<int>();

  // M[i][j] = 1 if ball i+1 is in box j+1
  std::vector<std::vector<dcp::Lin>> M(n, std::vector<dcp::Lin>(c));
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < c; ++j) M[i][j] = dcp::new_var(h, 0, 1);

  // a ball must be in exactly one box: M_i1 + M_i2 + M_i3 = 1 for every ball i
  for (int i = 0; i < n; ++i) {
    dcp::Lin one_box;
    for (int j = 0; j < c; ++j) one_box = one_box + M[i][j];
    dcp::add_row(h, one_box, 1, 1);
  }

  // for each x + y = z (x <= y, all in 1..n) and each box j, not all of balls x, y, z
  // are in box j: M_xj + M_yj + M_zj <= 2. When x = y the row has the coefficient 2 on x.
  for (int x = 1; x <= n; ++x)
    for (int y = x; x + y <= n; ++y) {
      int z = x + y;
      for (int j = 0; j < c; ++j)
        dcp::add_row(h, M[x - 1][j] + M[y - 1][j] + M[z - 1][j], -kHighsInf, 2);
    }

  // output: the box (1..c) of each ball
  std::vector<dcp::Lin> balls;
  for (int i = 0; i < n; ++i) {
    dcp::Lin box;
    for (int j = 0; j < c; ++j) box = box + static_cast<double>(j + 1) * M[i][j];
    balls.push_back(box);
  }
  out.add("balls", balls);
}
