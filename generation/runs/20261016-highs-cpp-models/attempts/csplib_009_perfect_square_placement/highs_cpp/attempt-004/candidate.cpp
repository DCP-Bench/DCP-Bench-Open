// Perfect square placement: pack squares with the given integer sides into a bigger square
// of side `base`, so that no two squares overlap, all borders are parallel to the big square,
// and the squares cover it exactly. Coordinates start from 0.
//
// Formulation: each square chooses one position (a, b) from the positions where it fits
// inside the big square. A binary p[i][a][b] says square i sits at (a, b). Every unit cell
// of the big square is covered by exactly one chosen square. This exact cover replaces the
// pairwise non-overlap disjunctions.
#include <cmath>
#include "dcp.h"

namespace {

struct Placement {
  int a;      // x of the lower-left corner
  int b;      // y of the lower-left corner
  HighsInt col;
};

}  // namespace

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int base = instance.at("base").get<int>();
  const std::vector<int> side = instance.at("sides").get<std::vector<int>>();
  const int n = static_cast<int>(side.size());

  // Symmetry: the largest square is anchored. Reflecting the packing in x and in y, and
  // transposing it, keep it a packing. So the largest square can be placed with a <= (base - s)/2,
  // b <= (base - s)/2 and a <= b.
  int big = 0;
  for (int i = 1; i < n; ++i)
    if (side[i] > side[big]) big = i;

  // Positions of each square. Each cell of the big square lists the placements covering it.
  std::vector<std::vector<Placement>> placements(n);
  std::vector<std::vector<HighsInt>> cover(static_cast<size_t>(base) * base);
  for (int i = 0; i < n; ++i) {
    const int s = side[i];
    const int top = base - s;
    for (int a = 0; a <= top; ++a) {
      for (int b = 0; b <= top; ++b) {
        if (i == big && (2 * a > top || 2 * b > top || a > b)) continue;
        const HighsInt col = h.getNumCol();
        dcp::new_var(h, 0, 1);
        placements[i].push_back({a, b, col});
        for (int u = a; u < a + s; ++u)
          for (int v = b; v < b + s; ++v) cover[static_cast<size_t>(u) * base + v].push_back(col);
      }
    }
  }

  // Each square takes exactly one position: one-hot over its placements.
  for (int i = 0; i < n; ++i) {
    std::vector<HighsInt> index;
    std::vector<double> value;
    for (const Placement& p : placements[i]) {
      index.push_back(p.col);
      value.push_back(1);
    }
    h.addRow(1, 1, static_cast<HighsInt>(index.size()), index.data(), value.data());
  }

  // Every unit cell of the big square is covered by exactly one square. Two squares
  // overlap if they share a cell, so this excludes overlaps and leaves no gap.
  for (int c = 0; c < base * base; ++c) {
    const auto& cols = cover[static_cast<size_t>(c)];
    std::vector<double> value(cols.size(), 1.0);
    h.addRow(1, 1, static_cast<HighsInt>(cols.size()), cols.data(), value.data());
  }

  // Coordinates: x_i and y_i are integer columns tied to the chosen position by one row each.
  std::vector<dcp::Lin> x, y;
  for (int i = 0; i < n; ++i) {
    dcp::Lin xi = dcp::new_var(h, 0, base - side[i]);
    dcp::Lin yi = dcp::new_var(h, 0, base - side[i]);
    x.push_back(xi);
    y.push_back(yi);
    std::vector<HighsInt> xindex{xi.terms[0].first}, yindex{yi.terms[0].first};
    std::vector<double> xvalue{1.0}, yvalue{1.0};
    for (const Placement& p : placements[i]) {
      xindex.push_back(p.col);
      xvalue.push_back(-static_cast<double>(p.a));
      yindex.push_back(p.col);
      yvalue.push_back(-static_cast<double>(p.b));
    }
    h.addRow(0, 0, static_cast<HighsInt>(xindex.size()), xindex.data(), xvalue.data());
    h.addRow(0, 0, static_cast<HighsInt>(yindex.size()), yindex.data(), yvalue.data());
  }

  // Squares with the same side are interchangeable. Among those other than the anchored
  // square, the one listed first has the smaller linear position: base * x + y is ordered.
  for (int i = 0; i < n; ++i) {
    for (int j = i + 1; j < n; ++j) {
      if (i == big || j == big || side[i] != side[j]) continue;
      dcp::add_row(h, base * x[i] + y[i] - base * x[j] - y[j], -kHighsInf, 0);
      break;
    }
  }

  // Satisfaction problem: no objective.
  out.add("x_coords", x);
  out.add("y_coords", y);
}
