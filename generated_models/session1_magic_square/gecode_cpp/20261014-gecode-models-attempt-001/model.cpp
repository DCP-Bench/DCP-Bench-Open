#include "dcp.h"

// Magic square: fill an n x n grid with the integers 1 to n^2, each once, so that
// every row, every column and both diagonals add up to n(n^2 + 1) / 2.
class MagicSquare : public dcp::Space {
 protected:
  IntVarArray cells;  // cells[r * n + c]: the number in row r, column c

 public:
  explicit MagicSquare(const json& instance) {
    int n = instance.at("n").get<int>();
    int total = n * n;

    // each cell holds an integer from 1 to n^2
    cells = IntVarArray(*this, total, 1, total);

    // each of the integers 1 to n^2 is used once
    distinct(*this, cells, IPL_DOM);

    // the common sum n(n^2 + 1) / 2, from the size n of the instance
    int magic = n * (n * n + 1) / 2;

    // every row adds up to the magic sum
    std::vector<IntVarArgs> rows(n);
    for (int r = 0; r < n; ++r)
      for (int c = 0; c < n; ++c) rows[r] << cells[r * n + c];
    for (int r = 0; r < n; ++r) linear(*this, rows[r], IRT_EQ, magic);

    // every column adds up to the magic sum
    for (int c = 0; c < n; ++c) {
      IntVarArgs column;
      for (int r = 0; r < n; ++r) column << cells[r * n + c];
      linear(*this, column, IRT_EQ, magic);
    }

    // the main diagonal adds up to the magic sum
    IntVarArgs main_diagonal, anti_diagonal;
    for (int i = 0; i < n; ++i) {
      main_diagonal << cells[i * n + i];
      anti_diagonal << cells[i * n + (n - 1 - i)];
    }
    linear(*this, main_diagonal, IRT_EQ, magic);
    // the other diagonal adds up to the magic sum too (for n = 1 both are one cell)
    linear(*this, anti_diagonal, IRT_EQ, magic);

    // branch on the cells in row-major order, most constrained first
    branch(*this, cells, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("square", rows);
  }

  MagicSquare(MagicSquare& s) : dcp::Space(s) { cells.update(*this, s.cells); }

  Gecode::Space* copy() override { return new MagicSquare(*this); }
};

DCP_MODEL(MagicSquare)
