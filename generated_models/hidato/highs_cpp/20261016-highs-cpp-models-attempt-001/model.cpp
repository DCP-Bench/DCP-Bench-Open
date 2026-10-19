// Hidato: fill the grid with the numbers 1..R*C (R rows, C columns, taken from the puzzle).
// The given numbers keep their cells. Consecutive numbers must touch horizontally,
// vertically or diagonally, and the numbers must be in increasing order.
// Print the solved puzzle as a grid of integers.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const json& puzzle = instance.at("puzzle");
  const int R = static_cast<int>(puzzle.size());
  const int C = static_cast<int>(puzzle[0].size());
  const int cells = R * C;  // every cell holds one number, so the numbers are 1..cells

  // given[c] is the number printed in cell c, 0 when the cell is empty
  std::vector<int> given(cells, 0);
  for (int i = 0; i < R; ++i)
    for (int j = 0; j < C; ++j) given[i * C + j] = puzzle[i][j].get<int>();

  // cell value columns: fixed where the puzzle gives a number
  std::vector<dcp::Lin> x(cells);
  for (int c = 0; c < cells; ++c) {
    double lo = given[c] > 0 ? given[c] : 1;
    double hi = given[c] > 0 ? given[c] : cells;
    x[c] = dcp::new_var(h, lo, hi);
  }

  // place[k][c] is 1 when number k sits in cell c; fixed for the given cells
  std::vector<std::vector<dcp::Lin>> place(cells + 1, std::vector<dcp::Lin>(cells));
  for (int k = 1; k <= cells; ++k)
    for (int c = 0; c < cells; ++c) {
      double lo = 0, hi = 1;
      if (given[c] > 0) lo = hi = (given[c] == k ? 1 : 0);
      place[k][c] = dcp::new_var(h, lo, hi);
    }

  // neighbours of each cell: the eight cells around it that lie in the grid
  std::vector<std::vector<int>> nb(cells);
  for (int i = 0; i < R; ++i)
    for (int j = 0; j < C; ++j)
      for (int di = -1; di <= 1; ++di)
        for (int dj = -1; dj <= 1; ++dj) {
          if (di == 0 && dj == 0) continue;
          int ni = i + di, nj = j + dj;
          if (ni < 0 || ni >= R || nj < 0 || nj >= C) continue;
          nb[i * C + j].push_back(ni * C + nj);
        }

  // every cell holds exactly one number
  for (int c = 0; c < cells; ++c) {
    dcp::Lin sum;
    for (int k = 1; k <= cells; ++k) sum = sum + place[k][c];
    dcp::add_row(h, sum, 1, 1);
  }

  // every number 1..cells is placed in exactly one cell
  for (int k = 1; k <= cells; ++k) {
    dcp::Lin sum;
    for (int c = 0; c < cells; ++c) sum = sum + place[k][c];
    dcp::add_row(h, sum, 1, 1);
  }

  // the value of each cell is the number placed in it
  for (int c = 0; c < cells; ++c) {
    dcp::Lin e = x[c];
    for (int k = 1; k <= cells; ++k) e = e - static_cast<double>(k) * place[k][c];
    dcp::add_row(h, e, 0, 0);
  }

  // if number k is in a cell, number k+1 is in one of its neighbours (k+1 touches k)
  for (int k = 1; k < cells; ++k)
    for (int c = 0; c < cells; ++c) {
      dcp::Lin e = -place[k][c];
      for (int n : nb[c]) e = e + place[k + 1][n];
      dcp::add_row(h, e, 0, kHighsInf);
    }

  std::vector<std::vector<dcp::Lin>> grid(R, std::vector<dcp::Lin>(C));
  for (int i = 0; i < R; ++i)
    for (int j = 0; j < C; ++j) grid[i][j] = x[i * C + j];
  out.add("x", grid);
}
