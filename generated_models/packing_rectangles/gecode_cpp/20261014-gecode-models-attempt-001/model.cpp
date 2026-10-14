#include "dcp.h"

// Rectangle packing: place n rectangles (widths and heights from the instance,
// no rotation) inside a bounding rectangle so that no two rectangles overlap and
// every rectangle lies inside the bounding rectangle. Minimise the area of the
// bounding rectangle.
class PackingRectangles : public dcp::Space {
 protected:
  IntVarArray pos_x;  // pos_x[i]: left edge of rectangle i, counted from 0
  IntVarArray pos_y;  // pos_y[i]: bottom edge of rectangle i, counted from 0
  IntVar total_x;     // width of the bounding rectangle
  IntVar total_y;     // height of the bounding rectangle

 public:
  explicit PackingRectangles(const json& instance) {
    std::vector<int> w = instance.at("widths").get<std::vector<int>>();
    std::vector<int> h = instance.at("heights").get<std::vector<int>>();
    int n = static_cast<int>(w.size());

    // sums and maxima of the data, used for the domains and the area bound
    int sum_w = 0, sum_h = 0, max_w = 0, max_h = 0, sum_area = 0;
    for (int i = 0; i < n; ++i) {
      sum_w += w[i];
      sum_h += h[i];
      max_w = (w[i] > max_w) ? w[i] : max_w;
      max_h = (h[i] > max_h) ? h[i] : max_h;
      sum_area += w[i] * h[i];
    }

    // The bounding rectangle is at least as wide as the widest item and at most
    // as wide as all items side by side. A packing with every item pushed left
    // and down has each edge within the sum of the widths (heights), so the
    // bounds do not cut off an optimum. The same holds for the heights.
    total_x = IntVar(*this, max_w, sum_w);
    total_y = IntVar(*this, max_h, sum_h);
    pos_x = IntVarArray(*this, n, 0, sum_w);
    pos_y = IntVarArray(*this, n, 0, sum_h);

    // every rectangle lies inside the bounding rectangle
    for (int i = 0; i < n; ++i) {
      rel(*this, pos_x[i] + w[i] <= total_x);
      rel(*this, pos_y[i] + h[i] <= total_y);
    }

    // no two rectangles overlap
    IntVarArgs xs, ys;
    for (int i = 0; i < n; ++i) {
      xs << pos_x[i];
      ys << pos_y[i];
    }
    nooverlap(*this, xs, IntArgs(w), ys, IntArgs(h));

    // redundant on each axis: the rectangles that cross a vertical line share
    // the height of the bounding rectangle, so their heights sum to at most
    // total_y; the same holds for horizontal lines and widths
    cumulative(*this, total_y, pos_x, IntArgs(w), IntArgs(h));
    cumulative(*this, total_x, pos_y, IntArgs(h), IntArgs(w));

    // the bounding rectangle holds all the items, so its area is at least the
    // sum of the item areas (redundant, implied by the data)
    IntVar area = expr(*this, total_x * total_y);
    rel(*this, area >= sum_area);

    // minimise the total area of the bounding rectangle
    minimize(area);

    // branch on the bounding rectangle first (it bounds every position), then on the positions
    branch(*this, total_x, INT_VAL_MIN());
    branch(*this, total_y, INT_VAL_MIN());
    branch(*this, pos_x, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, pos_y, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("pos_x", pos_x);
    output("pos_y", pos_y);
    output("total_x", total_x);
    output("total_y", total_y);
  }

  PackingRectangles(PackingRectangles& s) : dcp::Space(s) {
    pos_x.update(*this, s.pos_x);
    pos_y.update(*this, s.pos_y);
    total_x.update(*this, s.total_x);
    total_y.update(*this, s.total_y);
  }
  Gecode::Space* copy() override { return new PackingRectangles(*this); }
};

DCP_MODEL(PackingRectangles)
