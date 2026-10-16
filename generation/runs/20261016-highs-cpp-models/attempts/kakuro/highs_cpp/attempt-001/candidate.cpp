// Kakuro: fill each white cell of an n x n grid with a digit from 1 to 9 so that the
// digits of every entry (a run of white cells across or down) add up to its clue, and no
// digit is repeated within an entry. Black cells (the instance's "blanks") hold 0.
// Satisfaction problem: no objective.
#include <set>
#include <utility>
#include <vector>

#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int n = instance.at("n").get<int>();

  // Black cells, 1-based [row, column], taken from the instance.
  std::set<std::pair<int, int>> black;
  for (const auto& b : instance.at("blanks")) black.insert({b[0].get<int>(), b[1].get<int>()});

  // digit[r][c][v-1] = 1 when white cell (r, c) holds digit v. Indices are 0-based here.
  std::vector<std::vector<std::vector<dcp::Lin>>> digit(
      n, std::vector<std::vector<dcp::Lin>>(n));
  // value[r][c] = the digit in cell (r, c), 0 for black cells.
  std::vector<std::vector<dcp::Lin>> value(n, std::vector<dcp::Lin>(n, dcp::Lin(0.0)));

  // every white cell holds exactly one digit from 1 to 9
  for (int r = 1; r <= n; ++r) {
    for (int c = 1; c <= n; ++c) {
      if (black.count({r, c})) continue;
      dcp::Lin one_digit;
      dcp::Lin v_expr;
      for (int v = 1; v <= 9; ++v) {
        dcp::Lin b = dcp::new_var(h, 0, 1);
        digit[r - 1][c - 1].push_back(b);
        one_digit = one_digit + b;
        v_expr = v_expr + static_cast<double>(v) * b;
      }
      dcp::add_row(h, one_digit, 1, 1);
      value[r - 1][c - 1] = v_expr;
    }
  }

  // each clue's entry: the cells are listed as [row, column] after the sum
  for (const auto& entry : instance.at("problem")) {
    const int clue = entry[0].get<int>();
    std::vector<std::pair<int, int>> cells;
    for (size_t i = 1; i < entry.size(); ++i) {
      cells.push_back({entry[i][0].get<int>(), entry[i][1].get<int>()});
    }

    // the digits of the entry add up to the clue
    dcp::Lin total;
    for (const auto& rc : cells) total = total + value[rc.first - 1][rc.second - 1];
    dcp::add_row(h, total, clue, clue);

    // no digit is repeated within the entry: each digit is used at most once
    for (int v = 1; v <= 9; ++v) {
      dcp::Lin uses;
      for (const auto& rc : cells) uses = uses + digit[rc.first - 1][rc.second - 1][v - 1];
      dcp::add_row(h, uses, -kHighsInf, 1);
    }
  }

  // output x: the grid, 0 for black cells and the digit for white cells
  out.add("x", value);
}
