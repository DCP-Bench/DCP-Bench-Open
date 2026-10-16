// CSPLib 032: maximum density still life. Choose live/dead cells on an n x m active grid
// so that the pattern is stable under Conway's Game of Life and the number of live cells
// is maximal. Cells outside the grid are dead but still part of the board.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n").get<int>();
  int m = instance.at("m").get<int>();

  // The board is the active grid padded by one ring of dead cells (rows 0 and n+1,
  // columns 0 and m+1). Cells further out have no live neighbours, so they need no rules.
  // Active cell (i, j) is at 1-based position i in 1..n, j in 1..m.
  std::vector<std::vector<dcp::Lin>> cell(n + 2, std::vector<dcp::Lin>(m + 2));
  for (int i = 0; i < n + 2; ++i) {
    for (int j = 0; j < m + 2; ++j) {
      bool active = i >= 1 && i <= n && j >= 1 && j <= m;
      // a 1 is a live cell; the padding ring is fixed dead
      cell[i][j] = active ? dcp::new_var(h, 0, 1) : dcp::new_var(h, 0, 0);
    }
  }

  // Live neighbour count of every board cell: the sum of its up-to-8 neighbours
  std::vector<std::vector<dcp::Lin>> neighbours(n + 2, std::vector<dcp::Lin>(m + 2));
  for (int i = 0; i < n + 2; ++i) {
    for (int j = 0; j < m + 2; ++j) {
      dcp::Lin s;
      for (int di = -1; di <= 1; ++di) {
        for (int dj = -1; dj <= 1; ++dj) {
          if (di == 0 && dj == 0) continue;
          int ni = i + di, nj = j + dj;
          if (ni < 0 || ni > n + 1 || nj < 0 || nj > m + 1) continue;
          s = s + cell[ni][nj];
        }
      }
      neighbours[i][j] = s;
    }
  }

  // A live cell must have 2 or 3 live neighbours. The count is at most 8, so
  // s >= 2 x and s + 5 x <= 8 (x = 1 gives 2 <= s <= 3; x = 0 gives s <= 8).
  for (int i = 1; i <= n; ++i) {
    for (int j = 1; j <= m; ++j) {
      const dcp::Lin& x = cell[i][j];
      const dcp::Lin& s = neighbours[i][j];
      // a live cell has at least 2 live neighbours
      dcp::add_row(h, s - 2.0 * x, 0, kHighsInf);
      // a live cell has at most 3 live neighbours
      dcp::add_row(h, s + 5.0 * x, -kHighsInf, 8);
    }
  }

  // A dead cell, including a dead cell just outside the grid, must not have exactly 3
  // live neighbours. The binary b says whether the count is at least 4 (b = 1) or at
  // most 2 (b = 0), which rules out 3. When x = 1 the 8 and 4 terms make both rows
  // inactive, so the rule only bites on dead cells.
  for (int i = 0; i < n + 2; ++i) {
    for (int j = 0; j < m + 2; ++j) {
      const dcp::Lin& x = cell[i][j];
      const dcp::Lin& s = neighbours[i][j];
      dcp::Lin b = dcp::new_var(h, 0, 1);
      // count <= 2 when b = 0 (and <= 8 when b = 1)
      dcp::add_row(h, s - 6.0 * b - 8.0 * x, -kHighsInf, 2);
      // count >= 4 when b = 1
      dcp::add_row(h, s - 4.0 * b + 4.0 * x, 0, kHighsInf);
    }
  }

  // Objective: the number of live cells in the active grid
  dcp::Lin live;
  std::vector<std::vector<dcp::Lin>> grid(n, std::vector<dcp::Lin>(m));
  for (int i = 1; i <= n; ++i) {
    for (int j = 1; j <= m; ++j) {
      live = live + cell[i][j];
      grid[i - 1][j - 1] = cell[i][j];
    }
  }
  out.maximize(live);

  // Output: the n x m active area, 1 live and 0 dead
  out.add("grid", grid);
}
