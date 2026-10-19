// N-puzzle: slide the tiles of an n x n board until the start board becomes the end board.
// Tile 0 is the empty cell (the blank). Each step moves the blank to a neighbouring cell,
// which swaps it with the tile there, so every step changes the board.
// The output lists the N_STEPS boards, from the start board to the end board.
#include <vector>

#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  // the start and end boards and the number of boards come from the instance
  const auto start = instance.at("puzzle_start").get<std::vector<std::vector<int>>>();
  const auto goal = instance.at("puzzle_end").get<std::vector<std::vector<int>>>();
  const int steps = instance.at("N_STEPS").get<int>();
  const int n = static_cast<int>(start.size());  // the board is n x n
  const int cells = n * n;                       // cell p = row * n + col; tiles 0..cells-1

  auto neighbours = [n](int p) {
    std::vector<int> result;
    const int r = p / n, c = p % n;
    if (r > 0) result.push_back(p - n);
    if (r < n - 1) result.push_back(p + n);
    if (c > 0) result.push_back(p - 1);
    if (c < n - 1) result.push_back(p + 1);
    return result;
  };

  // x[t][p][k] = 1 when cell p holds tile k at board t
  std::vector<std::vector<std::vector<dcp::Lin>>> x(
      steps, std::vector<std::vector<dcp::Lin>>(cells, std::vector<dcp::Lin>(cells)));
  for (int t = 0; t < steps; ++t)
    for (int p = 0; p < cells; ++p)
      for (int k = 0; k < cells; ++k) x[t][p][k] = dcp::new_var(h, 0, 1);

  for (int t = 0; t < steps; ++t) {
    // each cell holds exactly one tile
    for (int p = 0; p < cells; ++p) {
      dcp::Lin one_tile;
      for (int k = 0; k < cells; ++k) one_tile = one_tile + x[t][p][k];
      dcp::add_row(h, one_tile, 1, 1);
    }
    // each tile sits on exactly one cell
    for (int k = 0; k < cells; ++k) {
      dcp::Lin one_cell;
      for (int p = 0; p < cells; ++p) one_cell = one_cell + x[t][p][k];
      dcp::add_row(h, one_cell, 1, 1);
    }
  }

  // the first board is the start board, the last board is the end board
  for (int p = 0; p < cells; ++p) {
    dcp::add_row(h, x[0][p][start[p / n][p % n]], 1, 1);
    dcp::add_row(h, x[steps - 1][p][goal[p / n][p % n]], 1, 1);
  }

  // move[t][p][q] = 1 when the blank goes from cell p to the neighbouring cell q at step t
  std::vector<std::vector<std::vector<dcp::Lin>>> move(
      steps > 0 ? steps - 1 : 0, std::vector<std::vector<dcp::Lin>>(cells, std::vector<dcp::Lin>(cells)));
  for (int t = 0; t + 1 < steps; ++t)
    for (int p = 0; p < cells; ++p)
      for (int q : neighbours(p)) move[t][p][q] = dcp::new_var(h, 0, 1);

  for (int t = 0; t + 1 < steps; ++t) {
    // the blank is in a cell exactly when it moves out of that cell
    for (int p = 0; p < cells; ++p) {
      dcp::Lin leaves;
      for (int q : neighbours(p)) leaves = leaves + move[t][p][q];
      dcp::add_row(h, leaves - x[t][p][0], 0, 0);
    }
    // the blank enters a cell exactly when it moves in from a neighbour
    for (int p = 0; p < cells; ++p) {
      dcp::Lin enters;
      for (int q : neighbours(p)) enters = enters + move[t][q][p];
      dcp::add_row(h, x[t + 1][p][0] - enters, 0, 0);
    }

    // g[p][q][k] = 1 when the blank moves from p to q and tile k moves from q into p
    // (g = move * tile is linearised with the three product rows)
    std::vector<std::vector<std::vector<dcp::Lin>>> g(
        cells, std::vector<std::vector<dcp::Lin>>(cells, std::vector<dcp::Lin>(cells)));
    for (int p = 0; p < cells; ++p)
      for (int q : neighbours(p))
        for (int k = 1; k < cells; ++k) {
          g[p][q][k] = dcp::new_var(h, 0, 1, false);
          dcp::add_row(h, g[p][q][k] - move[t][p][q], -kHighsInf, 0);
          dcp::add_row(h, g[p][q][k] - x[t][q][k], -kHighsInf, 0);
          dcp::add_row(h, g[p][q][k] - move[t][p][q] - x[t][q][k], -1, kHighsInf);
        }

    // a tile is moved, never created or lost: the tile count on each cell changes by the
    // tiles that arrive from neighbours and the tile that leaves
    for (int p = 0; p < cells; ++p)
      for (int k = 1; k < cells; ++k) {
        dcp::Lin change = x[t + 1][p][k] - x[t][p][k];
        for (int q : neighbours(p)) change = change - g[p][q][k] + g[q][p][k];
        dcp::add_row(h, change, 0, 0);
      }
  }

  // output: the tile number on each cell of each board
  std::vector<std::vector<std::vector<dcp::Lin>>> boards(
      steps, std::vector<std::vector<dcp::Lin>>(n, std::vector<dcp::Lin>(n)));
  for (int t = 0; t < steps; ++t)
    for (int p = 0; p < cells; ++p) {
      dcp::Lin tile;
      for (int k = 0; k < cells; ++k) tile = tile + static_cast<double>(k) * x[t][p][k];
      boards[t][p / n][p % n] = tile;
    }
  out.add("steps", boards);
}
