#include "dcp.h"

// Minesweeper: decide which unopened cells hold a mine, given the clue numbers
// of the opened cells. An opened cell is safe, and its number is how many of
// its eight neighbouring cells hold a mine.
class Minesweeper : public dcp::Space {
 protected:
  BoolVarArray mine;  // mine[r * cols + c] = 1 if cell (r, c) holds a mine

 public:
  explicit Minesweeper(const json& instance) {
    // the marker of an unopened cell in game_data (-1 in every instance)
    const int unopened = instance.at("X").get<int>();
    const auto& game = instance.at("game_data");
    const int rows = static_cast<int>(game.size());
    const int cols = static_cast<int>(game[0].size());

    mine = BoolVarArray(*this, rows * cols, 0, 1);

    // an opened cell is not a mine
    for (int r = 0; r < rows; ++r)
      for (int c = 0; c < cols; ++c)
        if (game[r][c].get<int>() != unopened)
          rel(*this, mine[r * cols + c], IRT_EQ, 0);

    // the number of mines around an opened cell is its clue
    for (int r = 0; r < rows; ++r)
      for (int c = 0; c < cols; ++c) {
        const int clue = game[r][c].get<int>();
        if (clue == unopened) continue;
        BoolVarArgs neighbours;
        for (int dr = -1; dr <= 1; ++dr)
          for (int dc = -1; dc <= 1; ++dc) {
            if (dr == 0 && dc == 0) continue;
            int nr = r + dr, nc = c + dc;
            if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) continue;
            neighbours << mine[nr * cols + nc];
          }
        linear(*this, neighbours, IRT_EQ, clue);
      }

    branch(*this, mine, BOOL_VAR_NONE(), BOOL_VAL_MIN());

    // mines[r] is row r of the board
    std::vector<BoolVarArgs> mines(rows);
    for (int r = 0; r < rows; ++r)
      for (int c = 0; c < cols; ++c) mines[r] << mine[r * cols + c];
    output("mines", mines);
  }

  Minesweeper(Minesweeper& s) : dcp::Space(s) { mine.update(*this, s.mine); }
  Gecode::Space* copy() override { return new Minesweeper(*this); }
};

DCP_MODEL(Minesweeper)
