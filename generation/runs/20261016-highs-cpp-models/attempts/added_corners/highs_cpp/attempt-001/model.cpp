// Added corners: enter the digits 1 through 8 in the 4 circles (corners) and 4 squares
// (edge midpoints) of a 3x3 frame with an empty centre, such that the number in each
// square equals the sum of the numbers in the adjoining circles. Output the 8 values
// in reading order (left to right, top to bottom).
//
// Positions in reading order: 0 TL circle, 1 top square, 2 TR circle,
// 3 left square, 4 right square, 5 BL circle, 6 bottom square, 7 BR circle.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;  // the puzzle has a fixed shape; no instance data is needed
  const int n = 8;

  // Each position takes a value in 1..8; the values are all different.
  // assignment binaries: y[i][v] = 1 means position i holds value v (v = 1..8)
  std::vector<dcp::Lin> x;
  std::vector<std::vector<dcp::Lin>> y(n, std::vector<dcp::Lin>(n + 1));
  for (int i = 0; i < n; i++) {
    x.push_back(dcp::new_var(h, 1, n));
    for (int v = 1; v <= n; v++) y[i][v] = dcp::new_var(h, 0, 1);
  }

  // // position i holds exactly one value
  for (int i = 0; i < n; i++) {
    dcp::Lin one_value;
    for (int v = 1; v <= n; v++) one_value = one_value + y[i][v];
    dcp::add_row(h, one_value, 1, 1);
  }

  // // the value of position i is the value chosen by its binaries
  for (int i = 0; i < n; i++) {
    dcp::Lin val = x[i];
    for (int v = 1; v <= n; v++) val = val - static_cast<double>(v) * y[i][v];
    dcp::add_row(h, val, 0, 0);
  }

  // // each value is used by exactly one position (the digits are all different)
  for (int v = 1; v <= n; v++) {
    dcp::Lin used_once;
    for (int i = 0; i < n; i++) used_once = used_once + y[i][v];
    dcp::add_row(h, used_once, 1, 1);
  }

  // // top square equals the sum of the top-left and top-right circles
  dcp::add_row(h, x[1] - x[0] - x[2], 0, 0);
  // // left square equals the sum of the top-left and bottom-left circles
  dcp::add_row(h, x[3] - x[0] - x[5], 0, 0);
  // // right square equals the sum of the top-right and bottom-right circles
  dcp::add_row(h, x[4] - x[2] - x[7], 0, 0);
  // // bottom square equals the sum of the bottom-left and bottom-right circles
  dcp::add_row(h, x[6] - x[5] - x[7], 0, 0);

  out.add("positions", x);
}
