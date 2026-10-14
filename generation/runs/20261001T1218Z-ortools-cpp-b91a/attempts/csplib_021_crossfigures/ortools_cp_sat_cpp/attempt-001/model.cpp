#include <string>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Crossfigures (CSPLib 21): the numerical equivalent of a crossword. Fill the
// 9 x 9 grid with digits so that every across and down entry is the number
// its clue describes; black squares hold 0.
// The problem has no instance data: the grid and the clues are the puzzle.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int n = 9;
  const int64_t max_number = 9999;  // entries have at most four digits

  // '#' marks a black square.
  const std::vector<std::string> grid = {
      "....#....", "..#...#..", ".#..#..#.", "....#....", "#.#####.#",
      "....#....", ".#..#..#.", "..#...#..", "....#....",
  };

  // M[i][j]: digit in row i, column j.
  std::vector<std::vector<IntVar>> M(n);
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) M[i].push_back(model.NewIntVar(Domain(0, 9)));

  // Black squares hold 0.
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j)
      if (grid[i][j] == '#') model.AddEquality(M[i][j], 0);

  // An entry of len digits starting at (row, col) (1-based), read across or
  // down, equals the number formed by those digits (leading zeros allowed).
  auto entry = [&](int len, int row, int col, bool across) {
    const IntVar number = model.NewIntVar(Domain(0, max_number));
    LinearExpr digits;
    int64_t weight = 1;
    for (int k = len - 1; k >= 0; --k) {
      const int i = row - 1 + (across ? 0 : k);
      const int j = col - 1 + (across ? k : 0);
      digits += weight * M[i][j];
      weight *= 10;
    }
    model.AddEquality(number, digits);
    return number;
  };
  // Across entries: number -> (length, row, column).
  const IntVar A1 = entry(4, 1, 1, true), A4 = entry(4, 1, 6, true), A7 = entry(2, 2, 1, true),
               A8 = entry(3, 2, 4, true), A9 = entry(2, 2, 8, true), A10 = entry(2, 3, 3, true),
               A11 = entry(2, 3, 6, true), A13 = entry(4, 4, 1, true), A15 = entry(4, 4, 6, true),
               A17 = entry(4, 6, 1, true), A20 = entry(4, 6, 6, true), A23 = entry(2, 7, 3, true),
               A24 = entry(2, 7, 6, true), A25 = entry(2, 8, 1, true), A27 = entry(3, 8, 4, true),
               A28 = entry(2, 8, 8, true), A29 = entry(4, 9, 1, true), A30 = entry(4, 9, 6, true);
  // Down entries.
  const IntVar D1 = entry(4, 1, 1, false), D2 = entry(2, 1, 2, false), D3 = entry(4, 1, 4, false),
               D4 = entry(4, 1, 6, false), D5 = entry(2, 1, 8, false), D6 = entry(4, 1, 9, false),
               D10 = entry(2, 3, 3, false), D12 = entry(2, 3, 7, false), D14 = entry(3, 4, 2, false),
               D16 = entry(3, 4, 8, false), D17 = entry(4, 6, 1, false), D18 = entry(2, 6, 3, false),
               D19 = entry(4, 6, 4, false), D20 = entry(4, 6, 6, false), D21 = entry(2, 6, 7, false),
               D22 = entry(4, 6, 9, false), D26 = entry(2, 8, 2, false), D28 = entry(2, 8, 8, false);

  // Squares and primes up to the largest four-digit number, for the clues
  // "a square number" and "a prime number".
  std::vector<int64_t> squares, primes;
  for (int64_t r = 1; r * r <= max_number; ++r) squares.push_back(r * r);
  std::vector<bool> composite(max_number + 1, false);
  for (int64_t v = 2; v <= max_number; ++v) {
    if (composite[v]) continue;
    primes.push_back(v);
    for (int64_t w = v * v; w <= max_number; w += v) composite[w] = true;
  }

  auto product = [&](const IntVar& target, const IntVar& u, const IntVar& v) {
    model.AddMultiplicationEquality(target, {u, v});
  };

  // Across clues. "X divided by k" is stated as k * entry == X, so the
  // division has to be exact.
  model.AddEquality(A1, 2 * A27);                               // 1: 27 across times two
  model.AddEquality(A4, D4 + 71);                               // 4: 4 down plus seventy-one
  model.AddEquality(A7, D18 + 4);                               // 7: 18 down plus four
  model.AddEquality(16 * A8, D6);                               // 8: 6 down divided by sixteen
  model.AddEquality(A9, D2 - 18);                               // 9: 2 down minus eighteen
  model.AddEquality(12 * A10, 6 * 144);                         // 10: dozen in six gross
  model.AddEquality(A11, D5 - 70);                              // 11: 5 down minus seventy
  product(A13, D26, A23);                                       // 13: 26 down times 23 across
  model.AddEquality(A15, D6 - 350);                             // 15: 6 down minus 350
  product(A17, A25, A23);                                       // 17: 25 across times 23 across
  model.AddLinearConstraint(A20, Domain::FromValues(squares));  // 20: a square number
  model.AddLinearConstraint(A23, Domain::FromValues(primes));   // 23: a prime number
  model.AddLinearConstraint(A24, Domain::FromValues(squares));  // 24: a square number
  model.AddEquality(17 * A25, A20);                             // 25: 20 across divided by seventeen
  model.AddEquality(4 * A27, D6);                               // 27: 6 down divided by four
  model.AddEquality(A28, 4 * 12);                               // 28: four dozen
  model.AddEquality(A29, 7 * 144);                              // 29: seven gross
  model.AddEquality(A30, D22 + 450);                            // 30: 22 down plus 450

  // Down clues.
  model.AddEquality(D1, A1 + 27);    // 1: 1 across plus twenty-seven
  model.AddEquality(D2, 5 * 12);     // 2: five dozen
  model.AddEquality(D3, A30 + 888);  // 3: 30 across plus 888
  model.AddEquality(D4, 2 * A17);    // 4: two times 17 across
  model.AddEquality(12 * D5, A29);   // 5: 29 across divided by twelve
  product(D6, A28, A23);             // 6: 28 across times 23 across
  model.AddEquality(D10, A10 + 4);   // 10: 10 across plus four
  model.AddEquality(D12, 3 * A24);   // 12: three times 24 across
  model.AddEquality(16 * D14, A13);  // 14: 13 across divided by sixteen
  model.AddEquality(D16, 15 * D28);  // 16: 28 down times fifteen
  model.AddEquality(D17, A13 - 399); // 17: 13 across minus 399
  model.AddEquality(18 * D18, A29);  // 18: 29 across divided by eighteen
  model.AddEquality(D19, D22 - 94);  // 19: 22 down minus ninety-four
  model.AddEquality(D20, A20 - 9);   // 20: 20 across minus nine
  model.AddEquality(D21, A25 - 52);  // 21: 25 across minus fifty-two
  model.AddEquality(D22, 6 * D20);   // 22: 20 down times six
  model.AddEquality(D26, 5 * A24);   // 26: five times 24 across
  model.AddEquality(D28, D21 + 27);  // 28: 21 down plus twenty-seven

  json out = json::array();
  for (int i = 0; i < n; ++i) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(M[i][j].index());
    out.push_back(row);
  }
  outputs = {{"M", out}};
}
