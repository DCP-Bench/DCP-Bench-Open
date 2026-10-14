// Perfect square placement: pack squares of the given sides into a big square of side
// base so that no two squares overlap and no space is left empty.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int base = instance.at("base");
  std::vector<int> sides = instance.at("sides").get<std::vector<int>>();
  int n = static_cast<int>(sides.size());

  // x[k], y[k] = lower left corner of square k; the square must lie inside the big square
  vec<IntVar*> x, y;
  for (int k = 0; k < n; ++k) {
    x.push(newIntVar(0, base - sides[k]));
    y.push(newIntVar(0, base - sides[k]));
  }

  // two squares never overlap: one lies left of the other, or right, or below, or above
  for (int k = 0; k < n; ++k) {
    for (int l = k + 1; l < n; ++l) {
      // square k lies to the left of square l
      BoolView left = newBoolVar();
      int_rel_reif(x[k], IRT_LE, x[l], left, -sides[k]);
      // square l lies to the left of square k
      BoolView right = newBoolVar();
      int_rel_reif(x[l], IRT_LE, x[k], right, -sides[l]);
      // square k lies below square l
      BoolView below = newBoolVar();
      int_rel_reif(y[k], IRT_LE, y[l], below, -sides[k]);
      // square l lies below square k
      BoolView above = newBoolVar();
      int_rel_reif(y[l], IRT_LE, y[k], above, -sides[l]);
      // one of the four separations must hold for the pair (k, l)
      vec<BoolView> separated;
      separated.push(left);
      separated.push(right);
      separated.push(below);
      separated.push(above);
      bool_clause(separated);
    }
  }

  // the squares together cover the big square: at every column, the heights of the squares
  // crossing it add up to at most base (redundant, but it prunes the search strongly)
  vec<int> dx, dy;
  for (int k = 0; k < n; ++k) {
    dx.push(sides[k]);
    dy.push(sides[k]);
  }
  cumulative(x, dx, dy, base);
  cumulative(y, dy, dx, base);

  // branch on the largest squares first, horizontal then vertical position
  vec<IntVar*> search;
  for (int k = 0; k < n; ++k) search.push(x[k]);
  for (int k = 0; k < n; ++k) search.push(y[k]);
  branch(search, VAR_SIZE_MIN, VAL_MIN);

  json xs = json::array(), ys = json::array();
  for (int k = 0; k < n; ++k) {
    xs.push_back(dcp::out(x[k]));
    ys.push_back(dcp::out(y[k]));
  }
  outputs = {{"x_coords", xs}, {"y_coords", ys}};
}
