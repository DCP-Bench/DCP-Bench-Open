// KenKen puzzle: fill an n x n grid (n from the instance) with the digits 1..n so that
// each row contains exactly one of each digit and each column contains exactly one of each digit.
// Each cage is a group of cells with a target number; the digits in the cage must achieve the
// target under one arithmetic operation (addition, subtraction, multiplication or division).
// The operation is not given: a two-cell cage may use any of the four, a cage of three or more
// cells may use addition or multiplication (subtraction and division are two-cell operations).
// Digits may repeat within a cage. The output x is the solved grid.
#include "dcp.h"

#include <algorithm>
#include <vector>

namespace {

// Does the digit tuple d satisfy the cage target under some allowed operation?
bool cage_ok(const std::vector<int>& d, int target) {
  const std::size_t k = d.size();
  if (k == 1) return d[0] == target;
  if (k == 2) {
    const int a = d[0], b = d[1];
    const int hi = std::max(a, b), lo = std::min(a, b);
    if (a + b == target) return true;
    if (hi - lo == target) return true;
    if (a * b == target) return true;
    if (hi % lo == 0 && hi / lo == target) return true;
    return false;
  }
  int sum = 0, prod = 1;
  for (int v : d) {
    sum += v;
    prod *= v;
  }
  return sum == target || prod == target;
}

}  // namespace

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int n = instance.at("n").get<int>();

  // Column helpers: integer column with bounds, and a row from index/value lists.
  auto add_int_col = [&](double lo, double hi) {
    const HighsInt col = h.getNumCol();
    h.addVar(lo, hi);
    h.changeColIntegrality(col, HighsVarType::kInteger);
    return col;
  };
  auto add_linear = [&](const std::vector<HighsInt>& idx, const std::vector<double>& val, double lo,
                        double hi) {
    h.addRow(lo, hi, static_cast<HighsInt>(idx.size()), idx.data(), val.data());
  };

  // Cell value columns x[r][c] in 1..n, and indicator columns y[r][c][v-1] = 1 iff cell (r,c) holds v.
  std::vector<std::vector<HighsInt>> xc(n, std::vector<HighsInt>(n));
  std::vector<std::vector<std::vector<HighsInt>>> yc(
      n, std::vector<std::vector<HighsInt>>(n, std::vector<HighsInt>(n)));
  for (int r = 0; r < n; ++r) {
    for (int c = 0; c < n; ++c) {
      xc[r][c] = add_int_col(1, n);
      for (int v = 0; v < n; ++v) yc[r][c][v] = add_int_col(0, 1);
    }
  }

  // each cell holds exactly one digit, and x is that digit
  for (int r = 0; r < n; ++r) {
    for (int c = 0; c < n; ++c) {
      std::vector<HighsInt> idx;
      std::vector<double> val;
      for (int v = 0; v < n; ++v) {
        idx.push_back(yc[r][c][v]);
        val.push_back(1);
      }
      add_linear(idx, val, 1, 1);

      idx.clear();
      val.clear();
      idx.push_back(xc[r][c]);
      val.push_back(1);
      for (int v = 0; v < n; ++v) {
        idx.push_back(yc[r][c][v]);
        val.push_back(-(v + 1));
      }
      add_linear(idx, val, 0, 0);
    }
  }

  // each row contains each digit exactly once
  for (int r = 0; r < n; ++r) {
    for (int v = 0; v < n; ++v) {
      std::vector<HighsInt> idx;
      std::vector<double> val;
      for (int c = 0; c < n; ++c) {
        idx.push_back(yc[r][c][v]);
        val.push_back(1);
      }
      add_linear(idx, val, 1, 1);
    }
  }

  // each column contains each digit exactly once
  for (int c = 0; c < n; ++c) {
    for (int v = 0; v < n; ++v) {
      std::vector<HighsInt> idx;
      std::vector<double> val;
      for (int r = 0; r < n; ++r) {
        idx.push_back(yc[r][c][v]);
        val.push_back(1);
      }
      add_linear(idx, val, 1, 1);
    }
  }

  // each cage: the digits in its cells achieve the cage target under one allowed operation
  // (a table over the digit tuples that satisfy the target, with one binary per tuple)
  const json& cages = instance.at("problem");
  for (const json& cage : cages) {
    const int target = cage.at(0).get<int>();
    const json& cells_json = cage.at(1);
    const std::size_t k = cells_json.size();
    if (k == 0) continue;

    std::vector<std::pair<int, int>> cells;
    for (const json& cell : cells_json) {
      cells.emplace_back(cell.at(0).get<int>() - 1, cell.at(1).get<int>() - 1);
    }

    // enumerate every digit tuple 1..n for the cells of this cage
    std::vector<std::vector<int>> tuples;
    std::vector<int> d(k, 1);
    while (true) {
      if (cage_ok(d, target)) tuples.push_back(d);
      std::size_t i = 0;
      while (i < k && d[i] == n) {
        d[i] = 1;
        ++i;
      }
      if (i == k) break;
      ++d[i];
    }

    // one binary per admissible tuple; exactly one tuple is chosen
    std::vector<HighsInt> tcol(tuples.size());
    for (std::size_t j = 0; j < tuples.size(); ++j) tcol[j] = add_int_col(0, 1);
    {
      std::vector<HighsInt> idx(tcol.begin(), tcol.end());
      std::vector<double> val(tuples.size(), 1);
      add_linear(idx, val, 1, 1);
    }

    // the chosen tuple gives each cell's digit: for each cell and digit, the tuples that put
    // that digit in the cell sum to the cell's indicator
    for (std::size_t i = 0; i < k; ++i) {
      const int r = cells[i].first;
      const int c = cells[i].second;
      for (int v = 1; v <= n; ++v) {
        std::vector<HighsInt> idx;
        std::vector<double> val;
        for (std::size_t j = 0; j < tuples.size(); ++j) {
          if (tuples[j][i] == v) {
            idx.push_back(tcol[j]);
            val.push_back(1);
          }
        }
        idx.push_back(yc[r][c][v - 1]);
        val.push_back(-1);
        add_linear(idx, val, 0, 0);
      }
    }
  }

  // the output is the solved grid
  std::vector<std::vector<dcp::Lin>> grid(n, std::vector<dcp::Lin>(n));
  for (int r = 0; r < n; ++r) {
    for (int c = 0; c < n; ++c) grid[r][c] = dcp::Lin::col(xc[r][c]);
  }
  out.add("x", grid);
}
