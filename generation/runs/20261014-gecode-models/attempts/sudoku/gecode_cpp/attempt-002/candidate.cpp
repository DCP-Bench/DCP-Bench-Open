#include "dcp.h"

// Sudoku: fill a 9x9 grid so that each row, each column and each 3x3 section
// contains every digit from 1 to 9 exactly once, keeping the given digits.
class Sudoku : public dcp::Space {
 protected:
  IntVarArray cells;  // cells[9 * r + c]: digit in row r, column c

 public:
  explicit Sudoku(const json& instance) {
    const json& given = instance.at("input_grid");  // 0 marks an empty cell
    const int n = 9;
    cells = IntVarArray(*this, n * n, 1, n);
    Matrix<IntVarArray> grid(cells, n, n);  // grid(c, r): column c, row r

    // every row contains all digits once
    for (int r = 0; r < n; ++r) distinct(*this, grid.row(r), IPL_DOM);

    // every column contains all digits once
    for (int c = 0; c < n; ++c) distinct(*this, grid.col(c), IPL_DOM);

    // every 3x3 section contains all digits once
    for (int br = 0; br < n; br += 3)
      for (int bc = 0; bc < n; bc += 3)
        distinct(*this, grid.slice(bc, bc + 3, br, br + 3), IPL_DOM);

    // the given digits of the puzzle stay where they are
    for (int r = 0; r < n; ++r)
      for (int c = 0; c < n; ++c) {
        int digit = given[r][c].get<int>();
        if (digit != 0) rel(*this, grid(c, r), IRT_EQ, digit);
      }

    branch(*this, cells, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("grid", grid);
  }

  Sudoku(Sudoku& s) : dcp::Space(s) { cells.update(*this, s.cells); }
  Gecode::Space* copy() override { return new Sudoku(*this); }
};

DCP_MODEL(Sudoku)
