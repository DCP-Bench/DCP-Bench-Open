#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Circular table (Averbach 1.2): three players X, Y, Z of different
// nationalities (American, English, French) sit around a round table and each
// passes cards to the person on their right. Y passed cards to the American,
// and X passed cards to the person who passed cards to the Frenchwoman.
// Seats are 0, 1, 2 around the table; seat (s + 1) mod 3 is right of seat s.
// The problem has no instance data: people and clues are part of the puzzle.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int n = 3;
  // Seat of each player and seat of each nationality.
  std::vector<IntVar> players, nationalities;
  for (int i = 0; i < n; ++i) {
    players.push_back(model.NewIntVar(Domain(0, n - 1)));
    nationalities.push_back(model.NewIntVar(Domain(0, n - 1)));
  }
  const IntVar &x = players[0], &y = players[1], &z = players[2];
  const IntVar &american = nationalities[0], &english = nationalities[1],
               &french = nationalities[2];

  // Each seat holds one player and one nationality.
  model.AddAllDifferent(players);
  model.AddAllDifferent(nationalities);

  // a sits right of b: a == (b + 1) mod 3.
  auto right_to = [&](const IntVar& a, const IntVar& b) {
    const IntVar next = model.NewIntVar(Domain(1, n));
    model.AddEquality(next, b + 1);
    model.AddModuloEquality(a, next, n);
  };

  // Y passed three hearts to the American: the American sits right of Y.
  right_to(american, y);
  // X passed cards to the person who passed to the Frenchwoman: X sits right
  // of the Frenchwoman.
  right_to(x, french);

  outputs = {{"x", x.index()},
             {"y", y.index()},
             {"z", z.index()},
             {"american", american.index()},
             {"english", english.index()},
             {"french", french.index()}};
}
