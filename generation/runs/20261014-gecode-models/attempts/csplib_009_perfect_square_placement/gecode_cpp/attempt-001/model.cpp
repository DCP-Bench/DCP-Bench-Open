#include "dcp.h"

// Perfect square placement (squared square): pack the squares whose sides are given
// into a square of side base so that no two squares overlap and every square's
// borders are parallel to the border of the packing square. The squares cover the
// packing square exactly, so there is no spare capacity.
//
// Instance fields: base (side of the packing square) and sides (side of each square).
class PerfectSquare : public dcp::Space {
 protected:
  IntVarArray x;  // x[i]: left coordinate of square i
  IntVarArray y;  // y[i]: bottom coordinate of square i

 public:
  explicit PerfectSquare(const json& instance) {
    int base = instance.at("base").get<int>();
    std::vector<int> side = instance.at("sides").get<std::vector<int>>();
    int n = static_cast<int>(side.size());

    IntArgs size(n);
    for (int i = 0; i < n; ++i) size[i] = side[i];

    // every square lies inside the packing square
    x = IntVarArray(*this, n);
    y = IntVarArray(*this, n);
    for (int i = 0; i < n; ++i) {
      x[i] = IntVar(*this, 0, base - side[i]);
      y[i] = IntVar(*this, 0, base - side[i]);
    }

    // no two squares overlap
    nooverlap(*this, x, size, y, size, IPL_DOM);

    // the squares cover the packing square exactly: each row and column of the
    // packing square is filled by squares, which is a redundant cumulative
    // on each axis
    cumulative(*this, base, x, size, size);
    cumulative(*this, base, y, size, size);

    branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, y, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("x_coords", x);
    output("y_coords", y);
  }

  PerfectSquare(PerfectSquare& s) : dcp::Space(s) {
    x.update(*this, s.x);
    y.update(*this, s.y);
  }
  Gecode::Space* copy() override { return new PerfectSquare(*this); }
};

DCP_MODEL(PerfectSquare)
