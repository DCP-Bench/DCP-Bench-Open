// Perfect square placement: pack squares with the given integer sides into a bigger square
// of side `base`, so that no two squares overlap, all borders are parallel to the big square,
// and the squares cover it exactly. Coordinates start from 0.
#include "dcp.h"

// Every unit line k (k = 0..base-1) across one direction is crossed by squares whose sides
// add up to base. pos[i] is the coordinate of square i along that direction, side[i] its size.
// on[i] = 1 forces square i to cover unit k: pos_i <= k and pos_i + s_i >= k + 1.
// Only that direction is forced, which is enough: the squares covering k must add up to base.
static void line_cover(Highs& h, const std::vector<dcp::Lin>& pos, const std::vector<double>& side, double base) {
  const int n = static_cast<int>(pos.size());
  for (int k = 0; k < static_cast<int>(base); ++k) {
    dcp::Lin total;
    for (int i = 0; i < n; ++i) {
      dcp::Lin on = dcp::new_var(h, 0, 1);
      // on = 1 implies pos_i <= k. Non-binding when on = 0 because pos_i <= base.
      dcp::add_row(h, pos[i] + base * on, -kHighsInf, k + base);
      // on = 1 implies pos_i >= k - s_i + 1. Non-binding when on = 0 because k - s_i + 1 - base < 0.
      dcp::add_row(h, pos[i] - base * on, k - side[i] + 1 - base, kHighsInf);
      total = total + side[i] * on;
    }
    // The squares crossing line k have sides that add up to the big square's side.
    dcp::add_row(h, total, base, base);
  }
}

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const double base = instance.at("base").get<double>();
  const std::vector<double> side = instance.at("sides").get<std::vector<double>>();
  const int n = static_cast<int>(side.size());

  // Each square i has its lower-left corner at (x_i, y_i). The square lies inside the big
  // square, so 0 <= x_i <= base - s_i and 0 <= y_i <= base - s_i.
  std::vector<dcp::Lin> x, y;
  for (int i = 0; i < n; ++i) {
    x.push_back(dcp::new_var(h, 0, base - side[i]));
    y.push_back(dcp::new_var(h, 0, base - side[i]));
  }

  // Two squares do not overlap: one lies left of the other, or right of it, or below it,
  // or above it. Each relation gets a binary. Every coordinate lies in 0..base, so
  // base is a valid big-M for each of the four relations.
  for (int i = 0; i < n; ++i) {
    for (int j = i + 1; j < n; ++j) {
      dcp::Lin left = dcp::new_var(h, 0, 1);    // 1: square i is left of square j
      dcp::Lin right = dcp::new_var(h, 0, 1);   // 1: square j is left of square i
      dcp::Lin below = dcp::new_var(h, 0, 1);   // 1: square i is below square j
      dcp::Lin above = dcp::new_var(h, 0, 1);   // 1: square j is below square i

      // square i left of square j: x_i + s_i <= x_j when left = 1.
      dcp::add_row(h, x[i] - x[j] + base * left, -kHighsInf, base - side[i]);
      // square j left of square i: x_j + s_j <= x_i when right = 1.
      dcp::add_row(h, x[j] - x[i] + base * right, -kHighsInf, base - side[j]);
      // square i below square j: y_i + s_i <= y_j when below = 1.
      dcp::add_row(h, y[i] - y[j] + base * below, -kHighsInf, base - side[i]);
      // square j below square i: y_j + s_j <= y_i when above = 1.
      dcp::add_row(h, y[j] - y[i] + base * above, -kHighsInf, base - side[j]);

      // The squares do not overlap: at least one of the four relations holds.
      dcp::add_row(h, left + right + below + above, 1, kHighsInf);
    }
  }

  // The squares fill the big square exactly, so every unit line in both directions
  // is crossed by squares whose sides add up to base (redundant, tightens the relaxation).
  line_cover(h, x, side, base);
  line_cover(h, y, side, base);

  // Satisfaction problem: no objective.
  out.add("x_coords", x);
  out.add("y_coords", y);
}
