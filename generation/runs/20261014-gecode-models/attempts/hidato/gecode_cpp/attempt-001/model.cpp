#include "dcp.h"

// Hidato: write the numbers 1 to R*C into an R x C grid so that each number
// touches the next one horizontally, vertically or diagonally. Some cells
// already hold their number; the other cells are to be filled in.
class Hidato : public dcp::Space {
 protected:
  IntVarArray x;    // x[c-1]: the number written in cell c (cells numbered row by row)
  IntVarArray y;    // y[v-1]: the cell that holds number v
  IntVarArray row;  // row[v-1]: the grid row of number v
  IntVarArray col;  // col[v-1]: the grid column of number v

 public:
  explicit Hidato(const json& instance) {
    const auto& puzzle = instance.at("puzzle");
    int R = puzzle.size();          // rows, from the instance
    int C = puzzle[0].size();       // columns, from the instance
    int N = R * C;                  // every cell holds one number, so the numbers are 1..N

    // row and column of each cell, indexed by cell number 1..N (index 0 unused)
    std::vector<int> rowOf(N + 1, 0), colOf(N + 1, 0);
    for (int c = 1; c <= N; ++c) {
      rowOf[c] = (c - 1) / C;
      colOf[c] = (c - 1) % C;
    }

    x = IntVarArray(*this, N, 1, N);
    y = IntVarArray(*this, N, 1, N);
    row = IntVarArray(*this, N, 0, R - 1);
    col = IntVarArray(*this, N, 0, C - 1);

    // each cell holds one number and each number sits in one cell
    channel(*this, x, 1, y, 1, IPL_DOM);

    // numbers given in the puzzle stay where they are
    for (int r = 0; r < R; ++r)
      for (int c = 0; c < C; ++c) {
        int v = puzzle[r][c].get<int>();
        if (v != 0) rel(*this, x[r * C + c] == v);
      }

    // the grid row and column of every number
    for (int v = 0; v < N; ++v) {
      rel(*this, row[v] == element(IntArgs(rowOf), y[v]));
      rel(*this, col[v] == element(IntArgs(colOf), y[v]));
    }

    // consecutive numbers touch: rows and columns differ by at most one
    for (int v = 0; v + 1 < N; ++v) {
      rel(*this, abs(row[v] - row[v + 1]) <= 1);
      rel(*this, abs(col[v] - col[v + 1]) <= 1);
    }

    // decide where each number goes, most constrained number first
    branch(*this, y, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    restarts(100);

    // the solved grid, one list per row
    output("x", Matrix<IntVarArray>(x, C, R));
  }

  Hidato(Hidato& s) : dcp::Space(s) {
    x.update(*this, s.x);
    y.update(*this, s.y);
    row.update(*this, s.row);
    col.update(*this, s.col);
  }
  Gecode::Space* copy() override { return new Hidato(*this); }
};

DCP_MODEL(Hidato)
