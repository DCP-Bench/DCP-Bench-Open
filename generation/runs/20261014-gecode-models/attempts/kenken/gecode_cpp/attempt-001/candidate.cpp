#include "dcp.h"

// KenKen: fill an n x n grid with the digits 1..n so that every row and every
// column holds each digit exactly once, and every cage (a bold group of cells
// with a target number) achieves its target with an arithmetic operation.
// The instance does not name the operation of each cage, so a cage is satisfied
// when some operation that fits its size reaches the target: sum or product for
// any cage, and also difference or exact quotient for a two-cell cage. A single
// cell cage fixes its cell to the target.
class KenKen : public dcp::Space {
 protected:
  int n;
  IntVarArray x;  // x[r * n + c]: digit in row r, column c (0-based)

  // Post one cage: its digits achieve the target by at least one operation.
  static void post_cage(Home home, const IntVarArgs& cells, int t) {
    int k = cells.size();
    if (k == 1) {
      // a single-cell cage: the digit is the target
      rel(home, cells[0] == t);
      return;
    }
    BoolVarArgs options;

    // the digits add up to the target
    IntVar total = expr(home, sum(cells));
    options << expr(home, total == t);

    // the digits multiply to the target (chain of products, small domains)
    IntVar prod = cells[0];
    for (int i = 1; i < k; ++i) prod = expr(home, prod * cells[i]);
    options << expr(home, prod == t);

    if (k == 2) {
      // two-cell cage: the larger digit minus the smaller is the target
      IntVar diff = expr(home, abs(cells[0] - cells[1]));
      options << expr(home, diff == t);

      // two-cell cage: the larger digit divided by the smaller is the target
      options << expr(home, cells[0] == t * cells[1]);
      options << expr(home, cells[1] == t * cells[0]);
    }

    // at least one of the operations reaches the target
    clause(home, BOT_OR, options, BoolVarArgs(), 1);
  }

 public:
  explicit KenKen(const json& instance) {
    n = instance.at("n").get<int>();
    x = IntVarArray(*this, n * n, 1, n);

    // every row holds each digit exactly once
    for (int r = 0; r < n; ++r) {
      IntVarArgs row;
      for (int c = 0; c < n; ++c) row << x[r * n + c];
      distinct(*this, row, IPL_DOM);
    }

    // every column holds each digit exactly once
    for (int c = 0; c < n; ++c) {
      IntVarArgs col;
      for (int r = 0; r < n; ++r) col << x[r * n + c];
      distinct(*this, col, IPL_DOM);
    }

    // each cage: its cells (1-based row and column in the data) reach its target
    for (const auto& cage : instance.at("problem")) {
      int target = cage[0].get<int>();
      IntVarArgs cells;
      for (const auto& rc : cage[1])
        cells << x[(rc[0].get<int>() - 1) * n + (rc[1].get<int>() - 1)];
      post_cage(*this, cells, target);
    }

    branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("x", Matrix<IntVarArray>(x, n, n));
  }

  KenKen(KenKen& s) : dcp::Space(s), n(s.n) { x.update(*this, s.x); }
  Gecode::Space* copy() override { return new KenKen(*this); }
};

DCP_MODEL(KenKen)
