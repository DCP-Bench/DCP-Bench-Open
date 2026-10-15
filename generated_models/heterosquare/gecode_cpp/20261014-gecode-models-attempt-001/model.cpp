#include "dcp.h"

// Heterosquare of order n: an n x n square of distinct integers from 1 to n^2
// whose row, column and diagonal sums are all different.
class Heterosquare : public dcp::Space {
 protected:
  int n;                // order of the square, from the instance
  IntVarArray cells;    // cells[r * n + c]: the entry in row r, column c
 public:
  explicit Heterosquare(const json& instance) {
    n = instance.at("n").get<int>();
    const int nn = n * n;
    cells = IntVarArray(*this, nn, 1, nn);

    // the elements of the square are distinct integers from 1 to n^2
    distinct(*this, cells, IPL_DOM);

    // every row, column and diagonal sum lies between the smallest and the
    // largest total of n distinct values from 1 to n^2
    const int lo = n * (n + 1) / 2;
    const int hi = n * nn - n * (n - 1) / 2;

    // posts a sum variable equal to the total of the given cells
    auto total_of = [this, lo, hi](const IntVarArgs& xs) {
      IntVar s(*this, lo, hi);
      linear(*this, xs, IRT_EQ, s, IPL_BND);
      return s;
    };

    IntVarArgs sums;

    // the row sums
    std::vector<IntVarArgs> rows(n);
    for (int r = 0; r < n; ++r) {
      for (int c = 0; c < n; ++c) rows[r] << cells[r * n + c];
      sums << total_of(rows[r]);
    }

    // the column sums
    for (int c = 0; c < n; ++c) {
      IntVarArgs col;
      for (int r = 0; r < n; ++r) col << cells[r * n + c];
      sums << total_of(col);
    }

    // the two diagonal sums: top left to bottom right, and top right to bottom left
    IntVarArgs diag, anti;
    for (int i = 0; i < n; ++i) {
      diag << cells[i * n + i];
      anti << cells[i * n + (n - 1 - i)];
    }
    sums << total_of(diag) << total_of(anti);

    // all row, column and diagonal sums are different
    distinct(*this, sums, IPL_DOM);

    // the search branches on the cells only: the sums are fixed once they are
    branch(*this, cells, INT_VAR_AFC_SIZE_MAX(0.99), INT_VAL_MIN());
    restarts(100);

    output("x", rows);
  }

  Heterosquare(Heterosquare& s) : dcp::Space(s), n(s.n) {
    cells.update(*this, s.cells);
  }

  Gecode::Space* copy() override { return new Heterosquare(*this); }
};

DCP_MODEL(Heterosquare)
