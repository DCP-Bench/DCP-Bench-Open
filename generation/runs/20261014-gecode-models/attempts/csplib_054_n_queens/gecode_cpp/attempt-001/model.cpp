#include "dcp.h"

// N-queens: place n queens on an n x n board so that no two queens attack each
// other. queens[i] is the column (1..n) of the queen in row i.
class NQueens : public dcp::Space {
 protected:
  IntVarArray queens;  // queens[i]: column of the queen in row i

 public:
  explicit NQueens(const json& instance) {
    int n = instance.at("n").get<int>();
    queens = IntVarArray(*this, n, 1, n);

    // no two queens share a column
    distinct(*this, queens, IPL_DOM);

    // no two queens share a diagonal going up-right: column + row is distinct
    IntArgs up(n), down(n);
    for (int i = 0; i < n; ++i) {
      up[i] = i;
      down[i] = -i;
    }
    distinct(*this, up, queens, IPL_DOM);

    // no two queens share a diagonal going down-right: column - row is distinct
    distinct(*this, down, queens, IPL_DOM);

    branch(*this, queens, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("queens", queens);
  }

  NQueens(NQueens& s) : dcp::Space(s) { queens.update(*this, s.queens); }
  Gecode::Space* copy() override { return new NQueens(*this); }
};

DCP_MODEL(NQueens)
