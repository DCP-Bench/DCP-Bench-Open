// Packing rectangles: place the given rectangles (widths[i] by heights[i], no rotation)
// inside one larger rectangle of size total_x by total_y, with no overlap and every
// rectangle inside the larger one; minimise the area total_x * total_y.
#include <algorithm>

#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  std::vector<int> w = instance.at("widths").get<std::vector<int>>();
  std::vector<int> ht = instance.at("heights").get<std::vector<int>>();
  const int n = static_cast<int>(w.size());

  // Data bounds: the larger rectangle is at least as wide as the widest item and at most
  // as wide as all items side by side (and the same for heights). Any packing can be
  // pushed to the left and bottom without growing, which keeps the total within these bounds.
  int sum_w = 0, sum_h = 0, max_w = 0, max_h = 0;
  for (int i = 0; i < n; ++i) {
    sum_w += w[i];
    sum_h += ht[i];
    max_w = std::max(max_w, w[i]);
    max_h = std::max(max_h, ht[i]);
  }
  const double Mx = sum_w;  // big-M for horizontal separation: no coordinate exceeds sum_w
  const double My = sum_h;  // big-M for vertical separation

  // total_x takes one value in max_w..sum_w, chosen by one indicator per value.
  dcp::Lin total_x, total_y, one_x, one_y;
  std::vector<dcp::Lin> bx, by;
  for (int k = max_w; k <= sum_w; ++k) {
    dcp::Lin b = dcp::new_var(h, 0, 1);
    bx.push_back(b);
    total_x = total_x + static_cast<double>(k) * b;
    one_x = one_x + b;
  }
  // exactly one width value is chosen for the larger rectangle
  dcp::add_row(h, one_x, 1, 1);
  for (int k = max_h; k <= sum_h; ++k) {
    dcp::Lin b = dcp::new_var(h, 0, 1);
    by.push_back(b);
    total_y = total_y + static_cast<double>(k) * b;
    one_y = one_y + b;
  }
  // exactly one height value is chosen for the larger rectangle
  dcp::add_row(h, one_y, 1, 1);

  // the area is the product of the chosen width and height: one binary z per pair of values;
  // z is forced to 1 for the chosen pair and the objective weighs each pair by its area
  dcp::Lin area;
  const int nx = static_cast<int>(bx.size());
  const int ny = static_cast<int>(by.size());
  for (int a = 0; a < nx; ++a) {
    for (int b = 0; b < ny; ++b) {
      dcp::Lin z = dcp::new_var(h, 0, 1);
      double product = static_cast<double>(max_w + a) * static_cast<double>(max_h + b);
      area = area + product * z;
      // the pair flag is 1 when both its width and its height are chosen
      dcp::add_row(h, z - bx[a] - by[b], -1, kHighsInf);
    }
  }

  // each rectangle's position: its left and bottom edges, counted from 0
  std::vector<dcp::Lin> pos_x, pos_y;
  for (int i = 0; i < n; ++i) {
    pos_x.push_back(dcp::new_var(h, 0, sum_w));
    pos_y.push_back(dcp::new_var(h, 0, sum_h));
  }

  // every rectangle lies inside the larger rectangle: x_i + width_i <= total_x and y_i + height_i <= total_y
  for (int i = 0; i < n; ++i) {
    dcp::add_row(h, pos_x[i] + static_cast<double>(w[i]) - total_x, -kHighsInf, 0);
    dcp::add_row(h, pos_y[i] + static_cast<double>(ht[i]) - total_y, -kHighsInf, 0);
  }

  // no two rectangles overlap: for each pair, one of four separations holds
  for (int i = 0; i < n; ++i) {
    for (int j = i + 1; j < n; ++j) {
      dcp::Lin left = dcp::new_var(h, 0, 1);   // i is left of j
      dcp::Lin right = dcp::new_var(h, 0, 1);  // i is right of j
      dcp::Lin below = dcp::new_var(h, 0, 1);  // i is below j
      dcp::Lin above = dcp::new_var(h, 0, 1);  // i is above j

      // i left of j: x_i + width_i <= x_j when left = 1
      dcp::add_row(h, pos_x[i] - pos_x[j] + Mx * left, -kHighsInf,
                   Mx - static_cast<double>(w[i]));
      // j left of i: x_j + width_j <= x_i when right = 1
      dcp::add_row(h, pos_x[j] - pos_x[i] + Mx * right, -kHighsInf,
                   Mx - static_cast<double>(w[j]));
      // i below j: y_i + height_i <= y_j when below = 1
      dcp::add_row(h, pos_y[i] - pos_y[j] + My * below, -kHighsInf,
                   My - static_cast<double>(ht[i]));
      // j below i: y_j + height_j <= y_i when above = 1
      dcp::add_row(h, pos_y[j] - pos_y[i] + My * above, -kHighsInf,
                   My - static_cast<double>(ht[j]));
      // at least one of the four separations holds
      dcp::add_row(h, left + right + below + above, 1, kHighsInf);
    }
  }

  out.add("pos_x", pos_x);
  out.add("pos_y", pos_y);
  out.add("total_x", total_x);
  out.add("total_y", total_y);
  // the objective: minimise the area of the larger rectangle
  out.minimize(area);
}
