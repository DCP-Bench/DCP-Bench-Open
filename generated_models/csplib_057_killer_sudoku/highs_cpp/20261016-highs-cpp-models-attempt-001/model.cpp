// csplib_057 killer sudoku: fill the n x n grid with digits 1..n so that every row,
// column and nonet holds each digit once, the cells of each cage sum to the total
// printed for that cage, and no digit appears twice in one cage.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n").get<int>();
  // The nonets are the square blocks of the grid; the side is the square root of n.
  int b = 0;
  while ((b + 1) * (b + 1) <= n) ++b;
  if (b * b != n) throw std::runtime_error("grid side must be a perfect square to have nonets");

  // y[r][c][v] = 1 when cell (r, c) holds digit v + 1 (0-based indices here).
  std::vector<std::vector<std::vector<dcp::Lin>>> y(
      n, std::vector<std::vector<dcp::Lin>>(n, std::vector<dcp::Lin>(n)));
  for (int r = 0; r < n; ++r)
    for (int c = 0; c < n; ++c)
      for (int v = 0; v < n; ++v) y[r][c][v] = dcp::new_var(h, 0, 1);

  // the value of a cell is the digit it holds; each cell holds exactly one digit
  std::vector<std::vector<dcp::Lin>> x(n, std::vector<dcp::Lin>(n));
  for (int r = 0; r < n; ++r)
    for (int c = 0; c < n; ++c) {
      dcp::Lin value, chosen;
      for (int v = 0; v < n; ++v) {
        value = value + static_cast<double>(v + 1) * y[r][c][v];
        chosen = chosen + y[r][c][v];
      }
      x[r][c] = value;
      dcp::add_row(h, chosen, 1, 1);
    }

  // each row contains every digit once
  for (int r = 0; r < n; ++r)
    for (int v = 0; v < n; ++v) {
      dcp::Lin count;
      for (int c = 0; c < n; ++c) count = count + y[r][c][v];
      dcp::add_row(h, count, 1, 1);
    }

  // each column contains every digit once
  for (int c = 0; c < n; ++c)
    for (int v = 0; v < n; ++v) {
      dcp::Lin count;
      for (int r = 0; r < n; ++r) count = count + y[r][c][v];
      dcp::add_row(h, count, 1, 1);
    }

  // each nonet (a b x b block of the grid) contains every digit once
  for (int br = 0; br < b; ++br)
    for (int bc = 0; bc < b; ++bc)
      for (int v = 0; v < n; ++v) {
        dcp::Lin count;
        for (int r = br * b; r < (br + 1) * b; ++r)
          for (int c = bc * b; c < (bc + 1) * b; ++c) count = count + y[r][c][v];
        dcp::add_row(h, count, 1, 1);
      }

  // each cage: the cells sum to the total printed for it, and no digit repeats in it.
  // The cage list holds [total, [[row, col], ...]] with 1-based coordinates.
  for (const auto& cage : instance.at("problem")) {
    int total = cage.at(0).get<int>();
    dcp::Lin sum;
    for (const auto& cell : cage.at(1)) {
      int r = cell.at(0).get<int>() - 1;
      int c = cell.at(1).get<int>() - 1;
      sum = sum + x[r][c];
    }
    dcp::add_row(h, sum, total, total);

    // no digit appears more than once in the cage
    for (int v = 0; v < n; ++v) {
      dcp::Lin count;
      for (const auto& cell : cage.at(1)) {
        int r = cell.at(0).get<int>() - 1;
        int c = cell.at(1).get<int>() - 1;
        count = count + y[r][c][v];
      }
      dcp::add_row(h, count, -kHighsInf, 1);
    }
  }

  // the solution is the filled grid; this is a satisfaction problem, so no objective
  out.add("x", x);
}
