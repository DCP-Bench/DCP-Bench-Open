// CSPLib 021 crossfigures: fill a 9x9 grid with digits so that every numbered clue,
// across and down, holds the number its clue states. The puzzle is fixed by the problem
// statement, so the grid and the clues are written here as data.
#include "dcp.h"

#include <sstream>
#include <string>
#include <utility>
#include <vector>

namespace {

constexpr int N = 9;

// X is a black cell, _ an empty white cell, and a number the clue number of a white cell.
const char* kGrid[N] = {
    "1 2 _ 3 X 4 _ 5 6",
    "7 _ X 8 _ _ X 9 _",
    "_ X 10 _ X 11 12 X _",
    "13 14 _ _ X 15 _ 16 _",
    "X _ X X X X X _ X",
    "17 _ 18 19 X 20 21 _ 22",
    "_ X 23 _ X 24 _ X _",
    "25 26 X 27 _ _ X 28 _",
    "29 _ _ _ X 30 _ _ _",
};

bool is_prime(int n) {
  for (int d = 2; d * d <= n; ++d)
    if (n % d == 0) return false;
  return n >= 2;
}

// A one-hot choice: a binary u that is 1 when the candidate with value y is chosen.
struct Choice {
  double y;
  dcp::Lin u;
};

// Exactly one candidate (value, image) is chosen; `total` equals the image of the chosen one.
std::vector<Choice> choose_one(Highs& h, const std::vector<std::pair<double, double>>& candidates,
                               const dcp::Lin& total) {
  std::vector<Choice> choices;
  dcp::Lin count, picked;
  for (const auto& [value, image] : candidates) {
    dcp::Lin u = dcp::new_var(h, 0, 1);
    choices.push_back({value, u});
    count = count + u;
    picked = picked + image * u;
  }
  dcp::add_row(h, count, 1, 1);
  dcp::add_row(h, total - picked, 0, 0);
  return choices;
}

// The product x * y, where x lies in [xlo, xhi] and y is the chosen candidate's value.
// Each q stands for x when its candidate is chosen and for 0 otherwise.
dcp::Lin times_one_hot(Highs& h, const dcp::Lin& x, double xlo, double xhi,
                       const std::vector<Choice>& choices) {
  dcp::Lin product;
  for (const auto& choice : choices) {
    const dcp::Lin& u = choice.u;
    dcp::Lin q = dcp::new_var(h, 0, xhi);
    dcp::add_row(h, q - xhi * u, -kHighsInf, 0);
    dcp::add_row(h, q - xlo * u, 0, kHighsInf);
    dcp::add_row(h, q - x - xlo * u, -kHighsInf, -xlo);
    dcp::add_row(h, q - x - xhi * u, -xhi, kHighsInf);
    product = product + choice.y * q;
  }
  return product;
}

void equal(Highs& h, const dcp::Lin& lhs, const dcp::Lin& rhs) {
  dcp::add_row(h, lhs - rhs, 0, 0);
}

}  // namespace

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;  // the puzzle is fixed by the problem statement; the instance carries no data

  // Cell kinds: -1 black, 0 white without a clue number, k white with clue number k.
  int kind[N][N];
  for (int r = 0; r < N; ++r) {
    std::istringstream row(kGrid[r]);
    for (int c = 0; c < N; ++c) {
      std::string token;
      row >> token;
      kind[r][c] = token == "X" ? -1 : (token == "_" ? 0 : std::stoi(token));
    }
  }
  auto white = [&](int r, int c) {
    return r >= 0 && r < N && c >= 0 && c < N && kind[r][c] != -1;
  };

  // A run is a maximal stretch of two or more white cells, read left to right (across) or
  // top to bottom (down). Its clue number is the number in its first cell.
  struct Run {
    int clue;
    std::vector<std::pair<int, int>> cells;
  };
  std::vector<Run> across_runs, down_runs;
  bool starts[N][N] = {};
  for (int r = 0; r < N; ++r)
    for (int c = 0; c < N; ++c) {
      if (!white(r, c)) continue;
      if (!white(r, c - 1)) {
        Run run{kind[r][c], {}};
        for (int k = c; white(r, k); ++k) run.cells.push_back({r, k});
        if (run.cells.size() >= 2) {
          starts[r][c] = true;
          across_runs.push_back(run);
        }
      }
      if (!white(r - 1, c)) {
        Run run{kind[r][c], {}};
        for (int k = r; white(k, c); ++k) run.cells.push_back({k, c});
        if (run.cells.size() >= 2) {
          starts[r][c] = true;
          down_runs.push_back(run);
        }
      }
    }

  // Each white cell holds one digit. The first digit of a number is not zero.
  dcp::Lin digit[N][N];
  for (int r = 0; r < N; ++r)
    for (int c = 0; c < N; ++c)
      if (white(r, c)) digit[r][c] = dcp::new_var(h, starts[r][c] ? 1 : 0, 9);

  // The value of a run: its digits read as a number, most significant digit first.
  auto value_of = [&](const Run& run) {
    dcp::Lin v;
    for (size_t k = 0; k < run.cells.size(); ++k) {
      auto [r, c] = run.cells[k];
      double place = 1;
      for (size_t p = k + 1; p < run.cells.size(); ++p) place *= 10;
      v = v + place * digit[r][c];
    }
    return v;
  };
  dcp::Lin across[31], down[31];  // across[k], down[k]: the answer to clue k
  for (const auto& run : across_runs) across[run.clue] = value_of(run);
  for (const auto& run : down_runs) down[run.clue] = value_of(run);

  // Across 23 is a prime number (two digits).
  std::vector<std::pair<double, double>> primes;
  for (int n = 10; n <= 99; ++n)
    if (is_prime(n)) primes.push_back({n, n});
  std::vector<Choice> prime_choice = choose_one(h, primes, across[23]);

  // Across 20 is a square number (four digits); across 24 is a square number (two digits).
  std::vector<std::pair<double, double>> squares4, squares2;
  for (int s = 1; s * s <= 9999; ++s) {
    if (s * s >= 1000) squares4.push_back({s * s, s * s});
    if (s * s >= 10 && s * s <= 99) squares2.push_back({s * s, s * s});
  }
  choose_one(h, squares4, across[20]);
  choose_one(h, squares2, across[24]);

  // Across 1: 27 across times two.
  equal(h, across[1], 2.0 * across[27]);
  // Across 4: 4 down plus seventy-one.
  equal(h, across[4], down[4] + 71.0);
  // Across 7: 18 down plus four.
  equal(h, across[7], down[18] + 4.0);
  // Across 8: 6 down divided by sixteen.
  equal(h, 16.0 * across[8], down[6]);
  // Across 9: 2 down minus eighteen.
  equal(h, across[9], down[2] - 18.0);
  // Across 10: dozen in six gross (six gross is 864, and 864 / 12 = 72).
  equal(h, across[10], 72.0);
  // Across 11: 5 down minus seventy.
  equal(h, across[11], down[5] - 70.0);
  // Across 13: 26 down times 23 across.
  equal(h, across[13], times_one_hot(h, down[26], 10, 99, prime_choice));
  // Across 15: 6 down minus 350.
  equal(h, across[15], down[6] - 350.0);
  // Across 17: 25 across times 23 across.
  equal(h, across[17], times_one_hot(h, across[25], 10, 99, prime_choice));
  // Across 25: 20 across divided by seventeen.
  equal(h, 17.0 * across[25], across[20]);
  // Across 27: 6 down divided by four.
  equal(h, 4.0 * across[27], down[6]);
  // Across 28: four dozen (48).
  equal(h, across[28], 48.0);
  // Across 29: seven gross (7 * 144 = 1008).
  equal(h, across[29], 1008.0);
  // Across 30: 22 down plus 450.
  equal(h, across[30], down[22] + 450.0);

  // Down 1: 1 across plus twenty-seven.
  equal(h, down[1], across[1] + 27.0);
  // Down 2: five dozen (60).
  equal(h, down[2], 60.0);
  // Down 3: 30 across plus 888.
  equal(h, down[3], across[30] + 888.0);
  // Down 4: two times 17 across.
  equal(h, down[4], 2.0 * across[17]);
  // Down 5: 29 across divided by twelve.
  equal(h, 12.0 * down[5], across[29]);
  // Down 6: 28 across times 23 across, with 28 across fixed at 48.
  equal(h, down[6], 48.0 * across[23]);
  // Down 10: 10 across plus four.
  equal(h, down[10], across[10] + 4.0);
  // Down 12: three times 24 across.
  equal(h, down[12], 3.0 * across[24]);
  // Down 14: 13 across divided by sixteen.
  equal(h, 16.0 * down[14], across[13]);
  // Down 16: 28 down times fifteen.
  equal(h, down[16], 15.0 * down[28]);
  // Down 17: 13 across minus 399.
  equal(h, down[17], across[13] - 399.0);
  // Down 18: 29 across divided by eighteen.
  equal(h, 18.0 * down[18], across[29]);
  // Down 19: 22 down minus ninety-four.
  equal(h, down[19], down[22] - 94.0);
  // Down 20: 20 across minus nine.
  equal(h, down[20], across[20] - 9.0);
  // Down 21: 25 across minus fifty-two.
  equal(h, down[21], across[25] - 52.0);
  // Down 22: 20 down times six.
  equal(h, down[22], 6.0 * down[20]);
  // Down 26: five times 24 across.
  equal(h, down[26], 5.0 * across[24]);
  // Down 28: 21 down plus twenty-seven.
  equal(h, down[28], down[21] + 27.0);

  // The declared output M: the digit of each white cell, 0 for a black cell.
  std::vector<std::vector<dcp::Lin>> M(N, std::vector<dcp::Lin>(N));
  for (int r = 0; r < N; ++r)
    for (int c = 0; c < N; ++c)
      M[r][c] = white(r, c) ? digit[r][c] : dcp::Lin(0);
  out.add("M", M);
}
