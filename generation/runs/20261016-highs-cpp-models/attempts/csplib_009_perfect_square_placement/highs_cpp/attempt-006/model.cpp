// Perfect square placement: pack squares with the given integer sides into a bigger square
// of side `base`, so that no two squares overlap, all borders are parallel to the big square,
// and the squares cover it exactly. Coordinates start from 0.
//
// Formulation: exact cover. p[i][a][b] = 1 when square i has its lower-left corner at (a, b).
// Each unit cell is covered by exactly one chosen placement. The marginals X[i][a] and Y[i][b]
// (the sums of p over b and over a) are binary columns, so the search can branch on a single
// coordinate, and each unit line is crossed by squares whose sides add up to base.
#include <algorithm>
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int base = instance.at("base").get<int>();
  const std::vector<int> side = instance.at("sides").get<std::vector<int>>();
  const int n = static_cast<int>(side.size());

  // Coordinates are subset sums of the other sides: a square starts at 0 or right after a chain
  // of squares that reaches it from the wall, so the chain's sides add up to its coordinate.
  std::vector<std::vector<char>> reach(n, std::vector<char>(base + 1, 0));
  for (int i = 0; i < n; ++i) {
    reach[i][0] = 1;
    for (int j = 0; j < n; ++j) {
      if (j == i) continue;
      for (int t = base; t >= side[j]; --t)
        if (reach[i][t - side[j]]) reach[i][t] = 1;
    }
  }

  // Columns: marginals first, then placements. cells[c] lists placements covering cell c.
  std::vector<std::vector<HighsInt>> X(n), Y(n);
  for (int i = 0; i < n; ++i) {
    const int top = base - side[i];
    X[i].assign(top + 1, -1);
    Y[i].assign(top + 1, -1);
    for (int a = 0; a <= top; ++a) {
      if (reach[i][a]) X[i][a] = dcp::new_var(h, 0, 1).terms[0].first;
      if (reach[i][a]) Y[i][a] = dcp::new_var(h, 0, 1).terms[0].first;
    }
  }

  std::vector<std::vector<HighsInt>> cells(static_cast<size_t>(base) * base);
  std::vector<std::vector<HighsInt>> xrow(n), yrow(n);  // placements feeding each marginal
  std::vector<std::vector<std::vector<HighsInt>>> xp(n), yp(n);
  for (int i = 0; i < n; ++i) {
    const int s = side[i];
    const int top = base - s;
    xp[i].assign(top + 1, {});
    yp[i].assign(top + 1, {});
    for (int a = 0; a <= top; ++a) {
      if (!reach[i][a]) continue;
      for (int b = 0; b <= top; ++b) {
        if (!reach[i][b]) continue;
        const HighsInt col = dcp::new_var(h, 0, 1).terms[0].first;
        xp[i][a].push_back(col);
        yp[i][b].push_back(col);
        for (int u = a; u < a + s; ++u)
          for (int v = b; v < b + s; ++v) cells[static_cast<size_t>(u) * base + v].push_back(col);
      }
    }
  }

  // Each square takes exactly one position, and the marginals are the sums of its placements.
  for (int i = 0; i < n; ++i) {
    const int top = base - side[i];
    std::vector<HighsInt> all;
    std::vector<double> ones;
    for (int a = 0; a <= top; ++a) {
      if (X[i][a] < 0) continue;
      all.push_back(X[i][a]);
      ones.push_back(1);
      // X[i][a] = sum over b of p[i][a][b]
      std::vector<HighsInt> index{X[i][a]};
      std::vector<double> value{1.0};
      for (HighsInt c : xp[i][a]) {
        index.push_back(c);
        value.push_back(-1);
      }
      h.addRow(0, 0, static_cast<HighsInt>(index.size()), index.data(), value.data());
    }
    h.addRow(1, 1, static_cast<HighsInt>(all.size()), all.data(), ones.data());
    for (int b = 0; b <= top; ++b) {
      if (Y[i][b] < 0) continue;
      std::vector<HighsInt> index{Y[i][b]};
      std::vector<double> value{1.0};
      for (HighsInt c : yp[i][b]) {
        index.push_back(c);
        value.push_back(-1);
      }
      h.addRow(0, 0, static_cast<HighsInt>(index.size()), index.data(), value.data());
    }
  }

  // Every unit cell of the big square is covered by exactly one square, so squares do not
  // overlap and leave no gap.
  for (int c = 0; c < base * base; ++c) {
    const auto& cols = cells[static_cast<size_t>(c)];
    std::vector<double> value(cols.size(), 1.0);
    h.addRow(1, 1, static_cast<HighsInt>(cols.size()), cols.data(), value.data());
  }

  // Every unit line, in both directions, is crossed by squares whose sides add up to base.
  for (int axis = 0; axis < 2; ++axis) {
    const auto& M = axis == 0 ? X : Y;
    for (int u = 0; u < base; ++u) {
      std::vector<HighsInt> index;
      std::vector<double> value;
      for (int i = 0; i < n; ++i) {
        const int top = base - side[i];
        for (int a = std::max(0, u - side[i] + 1); a <= std::min(u, top); ++a)
          if (M[i][a] >= 0) {
            index.push_back(M[i][a]);
            value.push_back(side[i]);
          }
      }
      h.addRow(base, base, static_cast<HighsInt>(index.size()), index.data(), value.data());
    }
  }

  // Coordinates: integer columns tied to the chosen position by one row each.
  std::vector<dcp::Lin> x, y;
  for (int axis = 0; axis < 2; ++axis) {
    const auto& M = axis == 0 ? X : Y;
    for (int i = 0; i < n; ++i) {
      const int top = base - side[i];
      dcp::Lin c = dcp::new_var(h, 0, top);
      std::vector<HighsInt> index{c.terms[0].first};
      std::vector<double> value{1.0};
      for (int a = 0; a <= top; ++a)
        if (M[i][a] >= 0) {
          index.push_back(M[i][a]);
          value.push_back(-a);
        }
      h.addRow(0, 0, static_cast<HighsInt>(index.size()), index.data(), value.data());
      (axis == 0 ? x : y).push_back(c);
    }
  }

  // Satisfaction problem: no objective.
  out.add("x_coords", x);
  out.add("y_coords", y);
}
