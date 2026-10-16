// Minesweeper: decide which unopened cells of the board contain a mine. The board is given
// as game_data, where -1 marks an unopened cell and a number is the clue on an opened cell.
// The clue on an opened cell is the number of mines among its adjacent cells.

#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  std::vector<std::vector<int>> board = instance.at("game_data").get<std::vector<std::vector<int>>>();
  int rows = static_cast<int>(board.size());
  int cols = rows > 0 ? static_cast<int>(board[0].size()) : 0;

  // mines[i][j] is 1 when the cell at row i, column j holds a mine
  std::vector<std::vector<dcp::Lin>> mines(rows, std::vector<dcp::Lin>(cols));
  for (int i = 0; i < rows; i++) {
    for (int j = 0; j < cols; j++) {
      if (board[i][j] < 0) {
        // an unopened cell is either a mine or not
        mines[i][j] = dcp::new_var(h, 0, 1);
      } else {
        // an opened cell (it shows a number) cannot be a mine
        mines[i][j] = dcp::Lin(0);
      }
    }
  }

  // the number on each opened cell is the count of mines in the cells adjacent to it
  for (int i = 0; i < rows; i++) {
    for (int j = 0; j < cols; j++) {
      if (board[i][j] < 0) continue;
      dcp::Lin adjacent_mines;
      for (int di = -1; di <= 1; di++) {
        for (int dj = -1; dj <= 1; dj++) {
          if (di == 0 && dj == 0) continue;
          int ni = i + di;
          int nj = j + dj;
          if (ni < 0 || ni >= rows || nj < 0 || nj >= cols) continue;
          adjacent_mines = adjacent_mines + mines[ni][nj];
        }
      }
      dcp::add_row(h, adjacent_mines, board[i][j], board[i][j]);
    }
  }

  out.add("mines", mines);
}
