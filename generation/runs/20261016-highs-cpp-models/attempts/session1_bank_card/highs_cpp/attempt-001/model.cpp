// Bank card PIN abcd (four digits a, b, c, d; each two-digit number ab, bc, cd, da
// is written with nonzero leading digit, so every digit is 1..9).
// Facts: no two digits are the same; the 2-digit number cd is 3 times the 2-digit
// number ab; the 2-digit number da is 2 times the 2-digit number bc.
// Print the PIN (a, b, c, d).
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;  // the PIN has no instance data

  // y[i][v] = 1 when digit i (0 = a, 1 = b, 2 = c, 3 = d) takes the value v.
  std::vector<std::vector<dcp::Lin>> y(4, std::vector<dcp::Lin>(10));
  for (int i = 0; i < 4; ++i)
    for (int v = 1; v <= 9; ++v) y[i][v] = dcp::new_var(h, 0, 1);

  // each digit is one value from 1 to 9, and the digit is that value
  dcp::Lin digit[4];
  for (int i = 0; i < 4; ++i) {
    // exactly one value per digit
    dcp::Lin one_hot;
    for (int v = 1; v <= 9; ++v) {
      one_hot = one_hot + y[i][v];
      digit[i] = digit[i] + (double)v * y[i][v];
    }
    dcp::add_row(h, one_hot, 1, 1);
  }

  // no two digits are the same: each value is used by at most one digit
  for (int v = 1; v <= 9; ++v) {
    dcp::Lin use;
    for (int i = 0; i < 4; ++i) use = use + y[i][v];
    dcp::add_row(h, use, -kHighsInf, 1);
  }

  // the 2-digit number cd is 3 times the 2-digit number ab
  dcp::add_row(h, 10.0 * digit[2] + digit[3] - 3.0 * (10.0 * digit[0] + digit[1]), 0, 0);

  // the 2-digit number da is 2 times the 2-digit number bc
  dcp::add_row(h, 10.0 * digit[3] + digit[0] - 2.0 * (10.0 * digit[1] + digit[2]), 0, 0);

  out.add("a", digit[0]);
  out.add("b", digit[1]);
  out.add("c", digit[2]);
  out.add("d", digit[3]);
}
