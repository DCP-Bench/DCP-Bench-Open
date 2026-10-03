#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Knight's tour: number the squares of an n x n chessboard 0..n*n-1 so that
// every square is visited exactly once and consecutive numbers are a knight's
// move apart (the tour is a path; it need not return to its start).
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();
  const int num_squares = n * n;
  const int dummy = num_squares;  // extra node that closes the path into a circuit

  // x[i][j] is the move number at which the knight is on square (i, j).
  std::vector<std::vector<IntVar>> x(n);
  std::vector<IntVar> all_squares;
  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) {
      x[i].push_back(model.NewIntVar(Domain(0, num_squares - 1)));
      all_squares.push_back(x[i][j]);
    }
  }

  // Each square is visited exactly once, so all move numbers are different.
  model.AddAllDifferent(all_squares);

  // Knight's moves: the next square is two steps in one direction and one in the other.
  const int moves[8][2] = {{2, 1}, {2, -1}, {-2, 1}, {-2, -1},
                           {1, 2}, {1, -2}, {-1, 2}, {-1, -2}};

  // The tour is stated as a path through the squares. The reference says that
  // a square numbered k has a knight's-move neighbour numbered k + 1 and one
  // numbered k - 1; CP-SAT is far faster at this with a circuit constraint
  // (a single cycle through every node) than with element-style lookups, so
  // each possible move is a Boolean arc "the knight goes from this square to
  // that one next". A dummy node joins the last square back to the first, so
  // the path becomes a cycle without requiring the knight to return.
  CircuitConstraint tour = model.AddCircuitConstraint();
  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) {
      const int from = i * n + j;
      for (const auto& move : moves) {
        const int ni = i + move[0], nj = j + move[1];
        if (ni < 0 || ni >= n || nj < 0 || nj >= n) continue;  // stay on the board
        const BoolVar goes_next = model.NewBoolVar();
        tour.AddArc(from, ni * n + nj, goes_next);
        // The next square is numbered one higher.
        model.AddEquality(x[ni][nj], x[i][j] + 1).OnlyEnforceIf(goes_next);
      }
      // The tour starts on the square numbered 0 (arc from the dummy node).
      const BoolVar is_first = model.NewBoolVar();
      tour.AddArc(dummy, from, is_first);
      model.AddEquality(x[i][j], 0).OnlyEnforceIf(is_first);
      // The tour ends on the square numbered n*n - 1 (arc to the dummy node).
      const BoolVar is_last = model.NewBoolVar();
      tour.AddArc(from, dummy, is_last);
      model.AddEquality(x[i][j], num_squares - 1).OnlyEnforceIf(is_last);
    }
  }

  json out = json::array();
  for (int i = 0; i < n; ++i) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(x[i][j].index());
    out.push_back(row);
  }
  outputs = {{"x", out}};
}
