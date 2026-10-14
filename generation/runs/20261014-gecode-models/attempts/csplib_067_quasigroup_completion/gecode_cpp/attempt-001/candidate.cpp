#include "dcp.h"

// Quasigroup completion: fill an order n table with the symbols 1..n so that every
// symbol occurs exactly once in each row and in each column, keeping the given cells.
class QuasigroupCompletion : public dcp::Space {
 protected:
  int n;                // order of the quasigroup (instance field N)
  IntVarArray cells;    // cells[c + n*r]: symbol in column c, row r

 public:
  explicit QuasigroupCompletion(const json& instance) {
    n = instance.at("N").get<int>();
    const json& start = instance.at("start");

    cells = IntVarArray(*this, n * n, 1, n);
    Matrix<IntVarArray> puzzle(cells, n, n);

    // each element from 1 to n occurs exactly once in every row
    for (int r = 0; r < n; ++r) {
      IntVarArgs row;
      for (int c = 0; c < n; ++c) row << puzzle(c, r);
      distinct(*this, row, IPL_DOM);
    }

    // each element from 1 to n occurs exactly once in every column
    for (int c = 0; c < n; ++c) {
      IntVarArgs col;
      for (int r = 0; r < n; ++r) col << puzzle(c, r);
      distinct(*this, col, IPL_DOM);
    }

    // the given cells keep their value (0 marks an empty cell)
    for (int r = 0; r < n; ++r)
      for (int c = 0; c < n; ++c) {
        int v = start[r][c].get<int>();
        if (v != 0) rel(*this, puzzle(c, r) == v);
      }

    // choose the cell with the fewest remaining symbols, try its smallest symbol first
    branch(*this, cells, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    // print the completed quasigroup, one list per row
    output("puzzle", puzzle);
  }

  QuasigroupCompletion(QuasigroupCompletion& s) : dcp::Space(s) {
    n = s.n;
    cells.update(*this, s.cells);
  }
  Gecode::Space* copy() override { return new QuasigroupCompletion(*this); }
};

DCP_MODEL(QuasigroupCompletion)
