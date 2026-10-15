#include "dcp.h"

// Futoshiki: place the digits 1 to n in an n x n grid so that each row and each
// column contains every digit once, the given digits are kept, and the
// inequality signs between neighbouring squares are honoured.
class Futoshiki : public dcp::Space {
 protected:
  int n;                // grid size, taken from the instance
  IntVarArray cell;     // cell[r * n + c]: digit in row r, column c (0-based)

 public:
  explicit Futoshiki(const json& instance)
      : n(static_cast<int>(instance.at("values").size())), cell(*this, n * n, 1, n) {
    const json& values = instance.at("values");
    const json& lt = instance.at("lt");

    // each row contains each of the digits 1 to n once
    for (int r = 0; r < n; ++r) {
      IntVarArgs row;
      for (int c = 0; c < n; ++c) row << cell[r * n + c];
      distinct(*this, row, IPL_DOM);
    }

    // each column contains each of the digits 1 to n once
    for (int c = 0; c < n; ++c) {
      IntVarArgs col;
      for (int r = 0; r < n; ++r) col << cell[r * n + c];
      distinct(*this, col, IPL_DOM);
    }

    // the given digits are kept (0 marks an empty square)
    for (int r = 0; r < n; ++r)
      for (int c = 0; c < n; ++c) {
        int v = values[r][c].get<int>();
        if (v != 0) rel(*this, cell[r * n + c] == v);
      }

    // inequality signs between neighbouring squares: the first square of each
    // pair holds the smaller digit (each entry is [row, column, row, column], 1-based)
    for (const auto& pair : lt) {
      int a = (pair[0].get<int>() - 1) * n + (pair[1].get<int>() - 1);
      int b = (pair[2].get<int>() - 1) * n + (pair[3].get<int>() - 1);
      rel(*this, cell[a], IRT_LE, cell[b]);
    }

    // branch on every square: most constrained square first, smallest digit first
    branch(*this, cell, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    // output the completed grid row by row
    std::vector<IntVarArgs> grid(n);
    for (int r = 0; r < n; ++r)
      for (int c = 0; c < n; ++c) grid[r] << cell[r * n + c];
    output("grid", grid);
  }

  Futoshiki(Futoshiki& s) : dcp::Space(s), n(s.n) {
    cell.update(*this, s.cell);
  }

  Gecode::Space* copy() override { return new Futoshiki(*this); }
};

DCP_MODEL(Futoshiki)
