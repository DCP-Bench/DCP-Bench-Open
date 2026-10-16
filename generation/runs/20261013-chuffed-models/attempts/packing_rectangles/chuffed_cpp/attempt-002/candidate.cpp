// Rectangle packing: place rectangles (no rotation) inside a larger rectangle without overlap,
// minimizing the area of the larger rectangle.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> widths = instance.at("widths").get<std::vector<int>>();
  std::vector<int> heights = instance.at("heights").get<std::vector<int>>();
  int n = static_cast<int>(widths.size());
  int sum_w = 0, sum_h = 0, max_w = 0, max_h = 0, sum_area = 0;
  for (int i = 0; i < n; ++i) {
    sum_w += widths[i];
    sum_h += heights[i];
    sum_area += widths[i] * heights[i];
    if (widths[i] > max_w) max_w = widths[i];
    if (heights[i] > max_h) max_h = heights[i];
  }

  // dimensions of the larger rectangle (at least the largest item, at most all items side by side)
  IntVar* total_x = newIntVar(max_w, sum_w);
  IntVar* total_y = newIntVar(max_h, sum_h);

  // pos_x[i], pos_y[i] = position of the lower-left corner of item i, counted from 0
  vec<IntVar*> pos_x, pos_y;
  for (int i = 0; i < n; ++i) {
    IntVar* px;
    IntVar* py;
    createVar(px, 0, sum_w - widths[i], true);
    createVar(py, 0, sum_h - heights[i], true);
    pos_x.push(px);
    pos_y.push(py);
  }

  // all items are within the boundaries of the larger rectangle
  for (int i = 0; i < n; ++i) {
    int_rel(pos_x[i], IRT_LE, total_x, -widths[i]);
    int_rel(pos_y[i], IRT_LE, total_y, -heights[i]);
  }

  // no two items overlap: one is left of, right of, below or above the other
  for (int i = 0; i < n; ++i) {
    for (int j = i + 1; j < n; ++j) {
      BoolView left = newBoolVar(), right = newBoolVar(), below = newBoolVar(), above = newBoolVar();
      int_rel_reif(pos_x[i], IRT_LE, pos_x[j], left, -widths[i]);    // x_i + w_i <= x_j
      int_rel_reif(pos_x[j], IRT_LE, pos_x[i], right, -widths[j]);   // x_j + w_j <= x_i
      int_rel_reif(pos_y[i], IRT_LE, pos_y[j], below, -heights[i]);  // y_i + h_i <= y_j
      int_rel_reif(pos_y[j], IRT_LE, pos_y[i], above, -heights[j]);  // y_j + h_j <= y_i
      vec<BoolView> apart;
      apart.push(left);
      apart.push(right);
      apart.push(below);
      apart.push(above);
      bool_clause(apart);
    }
  }

  // minimize the area of the larger rectangle (it cannot be smaller than the sum of the item areas)
  IntVar* area = newIntVar(sum_area, sum_w * sum_h);
  int_times(total_x, total_y, area);

  vec<IntVar*> decisions;
  decisions.push(total_x);
  decisions.push(total_y);
  for (int i = 0; i < n; ++i) decisions.push(pos_x[i]);
  for (int i = 0; i < n; ++i) decisions.push(pos_y[i]);
  branch(decisions, VAR_INORDER, VAL_MIN);
  optimize(area, OPT_MIN);

  json px = json::array(), py = json::array();
  for (int i = 0; i < n; ++i) {
    px.push_back(dcp::out(pos_x[i]));
    py.push_back(dcp::out(pos_y[i]));
  }
  outputs = {{"pos_x", px}, {"pos_y", py}, {"total_x", dcp::out(total_x)}, {"total_y", dcp::out(total_y)}};
}
