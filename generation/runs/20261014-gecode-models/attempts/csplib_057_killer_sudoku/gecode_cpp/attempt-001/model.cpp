#include "dcp.h"

// Killer sudoku: fill an n x n grid (n = 9) with the numbers 1 to 9 so that
// every row, column and nonet holds each number once, every cage sums to its
// printed total, and no number repeats inside a cage.
class KillerSudoku : public dcp::Space {
 protected:
  IntVarArray x;  // x[9*r + c]: the number in row r, column c (0-based)
  int n;          // grid side, from the instance
  int box;        // nonet side, sqrt(n)

 public:
  explicit KillerSudoku(const json& instance) {
    n = instance.at("n").get<int>();
    box = 1;
    while (box * box < n) ++box;

    // the grid: every cell holds a number from 1 to n
    x = IntVarArray(*this, n * n, 1, n);
    auto cell = [&](int r, int c) -> IntVar { return x[n * r + c]; };

    // each row holds every number once
    for (int r = 0; r < n; ++r) {
      IntVarArgs row;
      for (int c = 0; c < n; ++c) row << cell(r, c);
      distinct(*this, row, IPL_DOM);
    }

    // each column holds every number once
    for (int c = 0; c < n; ++c) {
      IntVarArgs col;
      for (int r = 0; r < n; ++r) col << cell(r, c);
      distinct(*this, col, IPL_DOM);
    }

    // each nonet (box x box block of cells) holds every number once
    for (int br = 0; br < n; br += box) {
      for (int bc = 0; bc < n; bc += box) {
        IntVarArgs nonet;
        for (int r = br; r < br + box; ++r)
          for (int c = bc; c < bc + box; ++c) nonet << cell(r, c);
        distinct(*this, nonet, IPL_DOM);
      }
    }

    // each cage: its cells sum to the printed total, and no number repeats in it
    // cage data: [total, [[row, col], ...]] with 1-based coordinates
    for (const auto& cage : instance.at("problem")) {
      int total = cage[0].get<int>();
      IntVarArgs cells;
      for (const auto& rc : cage[1]) {
        int r = rc[0].get<int>() - 1;
        int c = rc[1].get<int>() - 1;
        cells << cell(r, c);
      }

      // the cells of a cage add up to the number printed in its corner
      linear(*this, cells, IRT_EQ, total, IPL_DOM);

      // no number appears more than once in a cage
      distinct(*this, cells, IPL_DOM);
    }

    // search over all cells, smallest domain first
    branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    // output the grid as rows of numbers
    std::vector<IntVarArgs> rows(n);
    for (int r = 0; r < n; ++r)
      for (int c = 0; c < n; ++c) rows[r] << cell(r, c);
    output("x", rows);
  }

  KillerSudoku(KillerSudoku& s) : dcp::Space(s), n(s.n), box(s.box) {
    x.update(*this, s.x);
  }
  Gecode::Space* copy() override { return new KillerSudoku(*this); }
};

DCP_MODEL(KillerSudoku)
