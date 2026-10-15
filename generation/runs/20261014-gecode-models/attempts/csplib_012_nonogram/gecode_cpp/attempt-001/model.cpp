#include "dcp.h"

// Nonogram: shade squares of a rows x cols grid so that the blocks of consecutive
// shaded squares in every row and every column match the clues. A clue lists the
// block lengths in order; zero entries are padding.
// Output: board[r][c] is 1 for a shaded square and 0 for an unshaded one.

// The blocks of a clue, without the zero padding.
static std::vector<int> blocks_of(const json& clue) {
  std::vector<int> blocks;
  for (const auto& v : clue) {
    int b = v.get<int>();
    if (b > 0) blocks.push_back(b);
  }
  return blocks;
}

// Post the line constraint: the cells of one row or column form the clue's blocks,
// each a run of 1s, separated by at least one 0, with any number of 0s at the ends.
// The pattern is a regular language, so it is posted as a DFA.
static void post_clue(Gecode::Space& home, const IntVarArgs& line, const std::vector<int>& blocks) {
  REG re = *REG(0);  // leading unshaded squares
  for (std::size_t k = 0; k < blocks.size(); ++k) {
    if (k > 0) re = re + (+REG(0));  // at least one gap between two blocks
    re = re + REG(1)(blocks[k], blocks[k]);  // a block of exactly blocks[k] shaded squares
  }
  re = re + *REG(0);  // trailing unshaded squares
  DFA d(re);
  extensional(home, line, d);
}

class Nonogram : public dcp::Space {
 protected:
  IntVarArray cell;  // cell[r * cols + c]: 1 if the square is shaded

 public:
  explicit Nonogram(const json& instance) {
    int rows = instance.at("rows").get<int>();
    int cols = instance.at("cols").get<int>();
    const json& row_rules = instance.at("row_rules");
    const json& col_rules = instance.at("col_rules");

    cell = IntVarArray(*this, rows * cols, 0, 1);
    Matrix<IntVarArray> board(cell, cols, rows);

    // the blocks in each row match the row clue
    for (int r = 0; r < rows; ++r) {
      IntVarArgs line;
      for (int c = 0; c < cols; ++c) line << cell[r * cols + c];
      post_clue(*this, line, blocks_of(row_rules[r]));
    }

    // the blocks in each column match the column clue
    for (int c = 0; c < cols; ++c) {
      IntVarArgs line;
      for (int r = 0; r < rows; ++r) line << cell[r * cols + c];
      post_clue(*this, line, blocks_of(col_rules[c]));
    }

    branch(*this, cell, INT_VAR_AFC_SIZE_MAX(0.99), INT_VAL_MIN());
    restarts(100);
    output("board", board);
  }

  Nonogram(Nonogram& s) : dcp::Space(s) { cell.update(*this, s.cell); }
  Gecode::Space* copy() override { return new Nonogram(*this); }
};

DCP_MODEL(Nonogram)
