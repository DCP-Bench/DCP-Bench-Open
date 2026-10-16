// Vessel loading (CSPLib prob008): place every container as an axis-parallel rectangle
// on the deck, without overlaps and with the minimum separations between container classes.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int W = instance.at("deck_width").get<int>();
  const int L = instance.at("deck_length").get<int>();
  const int n = instance.at("n_containers").get<int>();
  const std::vector<int> w = instance.at("width").get<std::vector<int>>();
  const std::vector<int> l = instance.at("length").get<std::vector<int>>();
  const std::vector<int> cls = instance.at("classes").get<std::vector<int>>();
  const json& sepj = instance.at("separation");
  const int K = static_cast<int>(sepj.size());

  // largest separation in the data, used to size the big-M constants
  int S = 0;
  for (int a = 0; a < K; ++a)
    for (int b = 0; b < K; ++b) {
      const int v = sepj.at(a).at(b).get<int>();
      if (v > S) S = v;
    }
  const double Mx = W + S;  // horizontal big-M: right edge minus left edge is at most W
  const double My = L + S;  // vertical big-M

  // position of each container: left and bottom edge, and a rotation flag (1 = turned 90 degrees)
  std::vector<dcp::Lin> left(n), bottom(n), rot(n);
  for (int i = 0; i < n; ++i) {
    left[i] = dcp::new_var(h, 0, W);
    bottom[i] = dcp::new_var(h, 0, L);
    rot[i] = dcp::new_var(h, 0, 1);
  }

  // footprint of each container: its width is w when upright and l when turned, and its length the other way round
  std::vector<dcp::Lin> right(n), top(n);
  for (int i = 0; i < n; ++i) {
    right[i] = left[i] + double(w[i]) + double(l[i] - w[i]) * rot[i];
    top[i] = bottom[i] + double(l[i]) + double(w[i] - l[i]) * rot[i];
  }

  // every container lies within the deck
  for (int i = 0; i < n; ++i) {
    dcp::add_row(h, right[i], -kHighsInf, W);
    dcp::add_row(h, top[i], -kHighsInf, L);
  }

  // every pair of containers is separated, on the left, on the right, below or above, by at least the
  // separation between their classes; a separation of 0 is plain non-overlap
  for (int i = 0; i < n; ++i) {
    for (int j = i + 1; j < n; ++j) {
      const int s = sepj.at(cls[i] - 1).at(cls[j] - 1).get<int>();
      dcp::Lin i_left_of_j = dcp::new_var(h, 0, 1);
      dcp::Lin j_left_of_i = dcp::new_var(h, 0, 1);
      dcp::Lin i_below_j = dcp::new_var(h, 0, 1);
      dcp::Lin j_below_i = dcp::new_var(h, 0, 1);

      // one of the four relations holds
      dcp::add_row(h, i_left_of_j + j_left_of_i + i_below_j + j_below_i, 1, kHighsInf);

      // i left of j: the right edge of i plus the separation is at or before the left edge of j
      dcp::add_row(h, right[i] - left[j] + Mx * i_left_of_j, -kHighsInf, Mx - s);
      // j left of i
      dcp::add_row(h, right[j] - left[i] + Mx * j_left_of_i, -kHighsInf, Mx - s);
      // i below j: the top edge of i plus the separation is at or before the bottom edge of j
      dcp::add_row(h, top[i] - bottom[j] + My * i_below_j, -kHighsInf, My - s);
      // j below i
      dcp::add_row(h, top[j] - bottom[i] + My * j_below_i, -kHighsInf, My - s);
    }
  }

  // the declared outputs: one entry per container, in the instance's order
  std::vector<dcp::Lin> lefts(left.begin(), left.end());
  std::vector<dcp::Lin> rights(right.begin(), right.end());
  std::vector<dcp::Lin> bottoms(bottom.begin(), bottom.end());
  std::vector<dcp::Lin> tops(top.begin(), top.end());
  out.add("left", lefts);
  out.add("right", rights);
  out.add("bottom", bottoms);
  out.add("top", tops);
}
