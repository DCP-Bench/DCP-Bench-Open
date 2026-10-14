// Crossfigures: fill the 9 x 9 grid with digits so that every numbered across and down answer satisfies its clue.
// The instance has no data: the grid and the clues are the ones given in the problem statement.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // the grid, row by row: '#' is a black cell, '.' is a white cell (numbered cells are white)
  const int n = 9;
  const std::vector<std::string> grid = {
      "....#....",
      "..#...#..",
      ".#..#..#.",
      "....#....",
      "#.#####.#",
      "....#....",
      ".#..#..#.",
      "..#...#..",
      "....#...."};
  auto white = [&](int r, int c) {
    return r >= 0 && r < n && c >= 0 && c < n && grid[r][c] == '.';
  };

  // digit[r][c] is the digit written in the white cell at row r, column c (0-based)
  std::vector<std::vector<IntVar*>> digit(n, std::vector<IntVar*>(n, nullptr));
  for (int r = 0; r < n; ++r) {
    for (int c = 0; c < n; ++c) {
      if (white(r, c)) createVar(digit[r][c], 0, 9);
    }
  }

  // an answer is a run of at least two white cells read across or down; a run of length L is an L-digit number with no leading zero
  auto make_answer = [&](const std::vector<IntVar*>& cells) {
    int len = static_cast<int>(cells.size());
    int lo = 1;
    for (int k = 1; k < len; ++k) lo *= 10;
    IntVar* value = newIntVar(lo, lo * 10 - 1);
    vec<int> weight;
    vec<IntVar*> ds;
    for (int k = 0; k < len; ++k) {
      int w = 1;
      for (int e = len - 1 - k; e > 0; --e) w *= 10;
      weight.push(w);
      ds.push(cells[k]);
    }
    // the answer is the number written by its digits
    int_linear(weight, ds, IRT_EQ, value);
    return value;
  };

  // answers are numbered in reading order, as the cells of the grid are; across[k] and down[k] are the answers with number k
  std::vector<IntVar*> across(40, nullptr);
  std::vector<IntVar*> down(40, nullptr);
  int number = 0;
  for (int r = 0; r < n; ++r) {
    for (int c = 0; c < n; ++c) {
      if (!white(r, c)) continue;
      bool starts_across = !white(r, c - 1) && white(r, c + 1);
      bool starts_down = !white(r - 1, c) && white(r + 1, c);
      if (!starts_across && !starts_down) continue;
      ++number;
      if (starts_across) {
        std::vector<IntVar*> cells;
        for (int cc = c; white(r, cc); ++cc) cells.push_back(digit[r][cc]);
        across[number] = make_answer(cells);
      }
      if (starts_down) {
        std::vector<IntVar*> cells;
        for (int rr = r; white(rr, c); ++rr) cells.push_back(digit[rr][c]);
        down[number] = make_answer(cells);
      }
    }
  }

  // helper: a * x + b * y = c
  auto lin2 = [&](IntVar* x, int a, IntVar* y, int b, int c) {
    vec<int> coef;
    coef.push(a);
    coef.push(b);
    vec<IntVar*> xs;
    xs.push(x);
    xs.push(y);
    int_linear(coef, xs, IRT_EQ, c);
  };

  // across 20 and across 24 are square numbers: value = s * s for some s
  auto square = [&](IntVar* x) {
    IntVar* s = newIntVar(1, 100);
    int_times(s, s, x);
  };

  // across 23 is a prime number (a two-digit answer, so the primes from 10 to 99)
  auto prime2 = [&](IntVar* x) {
    vec<vec<int>> rows;
    for (int p = 10; p <= 99; ++p) {
      bool is_prime = true;
      for (int d = 2; d * d <= p; ++d) {
        if (p % d == 0) is_prime = false;
      }
      if (is_prime) {
        rows.push();
        rows.last().push(p);
      }
    }
    vec<IntVar*> xs;
    xs.push(x);
    table(xs, rows);
  };

  // across clues
  // across 1 is twice across 27
  lin2(across[1], 1, across[27], -2, 0);
  // across 4 is down 4 plus seventy-one
  lin2(across[4], 1, down[4], -1, 71);
  // across 7 is down 18 plus four
  lin2(across[7], 1, down[18], -1, 4);
  // across 8 is down 6 divided by sixteen (exact division, so down 6 = 16 x across 8)
  lin2(down[6], 1, across[8], -16, 0);
  // across 9 is down 2 minus eighteen
  lin2(across[9], 1, down[2], -1, -18);
  // across 10 is the number of dozen in six gross: 6 x 144 / 12
  int_rel(across[10], IRT_EQ, 72);
  // across 11 is down 5 minus seventy
  lin2(across[11], 1, down[5], -1, -70);
  // across 13 is down 26 times across 23
  int_times(down[26], across[23], across[13]);
  // across 15 is down 6 minus 350
  lin2(across[15], 1, down[6], -1, -350);
  // across 17 is across 25 times across 23
  int_times(across[25], across[23], across[17]);
  // across 20 is a square number
  square(across[20]);
  // across 23 is a prime number
  prime2(across[23]);
  // across 24 is a square number
  square(across[24]);
  // across 25 is across 20 divided by seventeen (exact division, so across 20 = 17 x across 25)
  lin2(across[20], 1, across[25], -17, 0);
  // across 27 is down 6 divided by four (exact division, so down 6 = 4 x across 27)
  lin2(down[6], 1, across[27], -4, 0);
  // across 28 is four dozen
  int_rel(across[28], IRT_EQ, 48);
  // across 29 is seven gross: 7 x 144
  int_rel(across[29], IRT_EQ, 1008);
  // across 30 is down 22 plus 450
  lin2(across[30], 1, down[22], -1, 450);

  // down clues
  // down 1 is across 1 plus twenty-seven
  lin2(down[1], 1, across[1], -1, 27);
  // down 2 is five dozen: 5 x 12
  int_rel(down[2], IRT_EQ, 60);
  // down 3 is across 30 plus 888
  lin2(down[3], 1, across[30], -1, 888);
  // down 4 is two times across 17
  lin2(down[4], 1, across[17], -2, 0);
  // down 5 is across 29 divided by twelve (exact division, so across 29 = 12 x down 5)
  lin2(across[29], 1, down[5], -12, 0);
  // down 6 is across 28 times across 23
  int_times(across[28], across[23], down[6]);
  // down 10 is across 10 plus four
  lin2(down[10], 1, across[10], -1, 4);
  // down 12 is three times across 24
  lin2(down[12], 1, across[24], -3, 0);
  // down 14 is across 13 divided by sixteen (exact division, so across 13 = 16 x down 14)
  lin2(across[13], 1, down[14], -16, 0);
  // down 16 is down 28 times fifteen
  lin2(down[16], 1, down[28], -15, 0);
  // down 17 is across 13 minus 399
  lin2(down[17], 1, across[13], -1, -399);
  // down 18 is across 29 divided by eighteen (exact division, so across 29 = 18 x down 18)
  lin2(across[29], 1, down[18], -18, 0);
  // down 19 is down 22 minus ninety-four
  lin2(down[19], 1, down[22], -1, -94);
  // down 20 is across 20 minus nine
  lin2(down[20], 1, across[20], -1, -9);
  // down 21 is across 25 minus fifty-two
  lin2(down[21], 1, across[25], -1, -52);
  // down 22 is down 20 times six
  lin2(down[22], 1, down[20], -6, 0);
  // down 26 is five times across 24
  lin2(down[26], 1, across[24], -5, 0);
  // down 28 is down 21 plus twenty-seven
  lin2(down[28], 1, down[21], -1, 27);

  // search on the digits in reading order
  vec<IntVar*> flat;
  for (int r = 0; r < n; ++r) {
    for (int c = 0; c < n; ++c) {
      if (digit[r][c] != nullptr) flat.push(digit[r][c]);
    }
  }
  branch(flat, VAR_INORDER, VAL_MIN);

  // black cells are output as 0
  json rows = json::array();
  for (int r = 0; r < n; ++r) {
    json row = json::array();
    for (int c = 0; c < n; ++c) {
      IntVar* v = digit[r][c] != nullptr ? digit[r][c] : getConstant(0);
      row.push_back(dcp::out(v));
    }
    rows.push_back(row);
  }
  outputs = {{"M", rows}};
}
