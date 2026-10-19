// Perfect square placement: pack squares with the given integer sides into a bigger square
// of side `base`, so that no two squares overlap, all borders are parallel to the big square,
// and the squares cover it exactly. Coordinates start from 0.
//
// Formulation: one-hot position variables per square and axis (X[i][a] = 1 when square i has
// x = a, Y[i][b] likewise). cx[i][u] = 1 when square i covers unit column u, cy[i][v] when it
// covers unit row v. z[i][u][v] = cx[i][u] * cy[i][v] says square i covers cell (u, v).
// Each cell is covered by exactly one square.
#include <algorithm>
#include "dcp.h"

namespace {

// One axis: one-hot positions, the coordinate column, and the coverage of each unit line.
struct Axis {
  std::vector<dcp::Lin> coord;
  std::vector<std::vector<HighsInt>> cover;  // cover[i][u]: column index, 1 when square i spans unit u
};

Axis make_axis(Highs& h, int base, const std::vector<int>& side) {
  const int n = static_cast<int>(side.size());
  Axis ax;
  // Squares in a perfect packing start at 0 or touch squares ending there, so a coordinate is
  // a subset sum of the other sides (the squares left of it along a chain).
  for (int i = 0; i < n; ++i) {
    std::vector<char> reach(base + 1, 0);
    reach[0] = 1;
    for (int j = 0; j < n; ++j) {
      if (j == i) continue;
      for (int t = base; t >= side[j]; --t)
        if (reach[t - side[j]]) reach[t] = 1;
    }
    const int top = base - side[i];
    std::vector<HighsInt> pos(top + 1, -1);
    std::vector<HighsInt> index;
    std::vector<double> value;
    for (int a = 0; a <= top; ++a) {
      if (!reach[a]) continue;
      dcp::Lin p = dcp::new_var(h, 0, 1);
      pos[a] = p.terms[0].first;
      index.push_back(pos[a]);
      value.push_back(1);
    }
    // Square i takes exactly one position on this axis.
    h.addRow(1, 1, static_cast<HighsInt>(index.size()), index.data(), value.data());

    // The coordinate column equals the chosen position.
    dcp::Lin c = dcp::new_var(h, 0, top);
    ax.coord.push_back(c);
    std::vector<HighsInt> ci{c.terms[0].first};
    std::vector<double> cv{1.0};
    for (int a = 0; a <= top; ++a)
      if (pos[a] >= 0) {
        ci.push_back(pos[a]);
        cv.push_back(-a);
      }
    h.addRow(0, 0, static_cast<HighsInt>(ci.size()), ci.data(), cv.data());

    // Square i spans unit u when its position lies in [u - s + 1, u].
    std::vector<HighsInt> span(base);
    for (int u = 0; u < base; ++u) {
      dcp::Lin s = dcp::new_var(h, 0, 1, false);
      span[u] = s.terms[0].first;
      std::vector<HighsInt> si{span[u]};
      std::vector<double> sv{1.0};
      for (int a = std::max(0, u - side[i] + 1); a <= std::min(u, top); ++a)
        if (pos[a] >= 0) {
          si.push_back(pos[a]);
          sv.push_back(-1);
        }
      h.addRow(0, 0, static_cast<HighsInt>(si.size()), si.data(), sv.data());
    }
    ax.cover.push_back(span);
  }
  // The squares crossing each unit line have sides adding up to base.
  for (int u = 0; u < base; ++u) {
    std::vector<HighsInt> index;
    std::vector<double> value;
    for (int i = 0; i < n; ++i) {
      index.push_back(ax.cover[i][u]);
      value.push_back(side[i]);
    }
    h.addRow(base, base, static_cast<HighsInt>(index.size()), index.data(), value.data());
  }
  return ax;
}

}  // namespace

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int base = instance.at("base").get<int>();
  const std::vector<int> side = instance.at("sides").get<std::vector<int>>();
  const int n = static_cast<int>(side.size());

  // Squares lie inside the big square, no two overlap, and together they cover it exactly.
  Axis X = make_axis(h, base, side);
  Axis Y = make_axis(h, base, side);

  // Every unit cell (u, v) is covered by exactly one square: z[i] = cx[i][u] AND cy[i][v].
  for (int u = 0; u < base; ++u) {
    for (int v = 0; v < base; ++v) {
      std::vector<HighsInt> index;
      std::vector<double> value;
      for (int i = 0; i < n; ++i) {
        dcp::Lin z = dcp::new_var(h, 0, 1, false);
        const HighsInt zc = z.terms[0].first;
        const HighsInt cx = X.cover[i][u], cy = Y.cover[i][v];
        // z <= cx
        HighsInt i1[2] = {zc, cx};
        double v1[2] = {1, -1};
        h.addRow(-kHighsInf, 0, 2, i1, v1);
        // z <= cy
        HighsInt i2[2] = {zc, cy};
        h.addRow(-kHighsInf, 0, 2, i2, v1);
        // z >= cx + cy - 1
        HighsInt i3[3] = {zc, cx, cy};
        double v3[3] = {1, -1, -1};
        h.addRow(-1, kHighsInf, 3, i3, v3);
        index.push_back(zc);
        value.push_back(1);
      }
      h.addRow(1, 1, static_cast<HighsInt>(index.size()), index.data(), value.data());
    }
  }

  // Satisfaction problem: no objective.
  out.add("x_coords", X.coord);
  out.add("y_coords", Y.coord);
}
