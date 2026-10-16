#include "dcp.h"

// Kakuro: fill every white cell with a digit 1..9 so that each clue's sum matches
// the clue and no digit repeats within a clue's entries. Blank cells hold 0.
class Kakuro : public dcp::Space {
 protected:
  IntVarArray cell;  // cell[r * n + c]: digit in row r, column c (0-based)
  int n;

 public:
  explicit Kakuro(const json& instance) {
    n = instance.at("n").get<int>();
    const auto& blanks = instance.at("blanks");
    const auto& clues = instance.at("problem");

    // every cell holds a digit 1..9, except the blank cells which hold 0
    cell = IntVarArray(*this, n * n, 0, 9);
    std::vector<bool> is_blank(n * n, false);
    for (const auto& b : blanks) is_blank[(b[0].get<int>() - 1) * n + (b[1].get<int>() - 1)] = true;
    for (int i = 0; i < n * n; ++i) {
      if (is_blank[i]) rel(*this, cell[i] == 0);
      else rel(*this, cell[i] >= 1);
    }

    // each clue is a run of white cells, across or down: the digits sum to the
    // clue, and no digit is repeated within the run
    for (const auto& clue : clues) {
      int sum = clue[0].get<int>();
      IntVarArgs run;
      for (std::size_t k = 1; k < clue.size(); ++k)
        run << cell[(clue[k][0].get<int>() - 1) * n + (clue[k][1].get<int>() - 1)];

      // the digits of the run are all different
      distinct(*this, run, IPL_DOM);

      // the digits of the run add up to the clue
      linear(*this, run, IRT_EQ, sum);
    }

    // search: fix the cells in order, smallest digit first
    branch(*this, cell, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    Matrix<IntVarArray> grid(cell, n, n);  // grid(c, r) is row r, column c
    output("x", grid);
  }

  Kakuro(Kakuro& s) : dcp::Space(s), n(s.n) {
    cell.update(*this, s.cell);
  }
  Gecode::Space* copy() override { return new Kakuro(*this); }
};

DCP_MODEL(Kakuro)
