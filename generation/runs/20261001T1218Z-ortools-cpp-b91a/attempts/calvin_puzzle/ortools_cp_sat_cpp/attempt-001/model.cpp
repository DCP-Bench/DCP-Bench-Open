#include <cstdlib>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Calvin's puzzle: fill an n x n grid with the numbers 1..n*n so that each
// number is reached from the previous one by a horizontal or vertical move of
// exactly three squares, or a diagonal move of exactly two squares.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();
  const int cells = n * n;

  // x[c] is the number written in cell c = i * n + j.
  // pos[k] is the cell holding number k + 1. The two are inverse permutations
  // of each other (shifted by one, since the numbers start at 1), which also
  // states that every number appears exactly once.
  std::vector<IntVar> value0, pos, x;
  for (int c = 0; c < cells; ++c) {
    value0.push_back(model.NewIntVar(Domain(0, cells - 1)));  // x[c] - 1
    pos.push_back(model.NewIntVar(Domain(0, cells - 1)));
  }
  model.AddInverseConstraint(value0, pos);
  for (int c = 0; c < cells; ++c) {
    const IntVar xc = model.NewIntVar(Domain(1, cells));
    model.AddEquality(xc, value0[c] + 1);
    x.push_back(xc);
  }

  // The allowed moves, as pairs of cells (from, to) that stay inside the grid:
  // a step (a, b) with |a| = 3, b = 0 or a = 0, |b| = 3 (two squares gap
  // horizontally or vertically), or |a| = |b| = 2 (one square gap diagonally).
  std::vector<std::vector<int64_t>> moves;
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j)
      for (int a = -3; a <= 3; ++a)
        for (int b = -3; b <= 3; ++b) {
          const bool straight = (std::abs(a) == 3 && b == 0) || (std::abs(b) == 3 && a == 0);
          const bool diagonal = std::abs(a) == 2 && std::abs(b) == 2;
          if (!straight && !diagonal) continue;
          const int ni = i + a, nj = j + b;
          if (ni < 0 || ni >= n || nj < 0 || nj >= n) continue;
          moves.push_back({i * n + j, ni * n + nj});
        }

  // Each number k + 1 is placed one allowed move away from number k.
  for (int k = 0; k + 1 < cells; ++k) {
    TableConstraint step = model.AddAllowedAssignments({pos[k], pos[k + 1]});
    for (const std::vector<int64_t>& m : moves) step.AddTuple(m);
  }

  json out = json::array();
  for (int i = 0; i < n; ++i) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(x[i * n + j].index());
    out.push_back(row);
  }
  outputs = {{"x", out}};
}
