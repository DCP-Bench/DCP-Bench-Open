#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Nontransitive dice for Rock-Paper-Scissors-Lizard-Spock: five six-faced dice
// with faces 1..12 such that each die beats exactly the two dice its choice
// beats in the game. Die A beats die B when a face of A is strictly larger
// than a face of B in more than half of the 36 face pairs.
// The problem has no instance data: the dice sizes and the game's "beats"
// relation are part of the puzzle.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int rock = 0, paper = 1, scissors = 2, lizard = 3, spock = 4;
  const int m = 5;   // number of dice
  const int n = 6;   // faces per die
  const int f = 12;  // largest face value

  // (winner, loser) for the ten "beats" relations of the game.
  const std::vector<std::pair<int, int>> edge = {
      {rock, scissors},  {rock, lizard},    {paper, rock},  {paper, spock},
      {scissors, paper}, {scissors, lizard}, {lizard, paper}, {lizard, spock},
      {spock, rock},     {spock, scissors},
  };

  // dice[i][j]: value of face j of die i. Values may repeat.
  std::vector<std::vector<IntVar>> dice(m);
  for (int i = 0; i < m; ++i)
    for (int j = 0; j < n; ++j) dice[i].push_back(model.NewIntVar(Domain(1, f)));

  // For each relation, the winner shows the larger face in more than half of
  // the n * n face pairs. wins is true only when that pair really is won (one
  // direction is enough, since the count is bounded from below).
  for (const auto& [winner, loser] : edge) {
    LinearExpr won;
    for (int x = 0; x < n; ++x)
      for (int y = 0; y < n; ++y) {
        const BoolVar wins = model.NewBoolVar();
        model.AddGreaterThan(dice[winner][x], dice[loser][y]).OnlyEnforceIf(wins);
        won += wins;
      }
    model.AddGreaterThan(won, (n * n) / 2);
  }

  json out = json::array();
  for (int i = 0; i < m; ++i) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(dice[i][j].index());
    out.push_back(row);
  }
  outputs = {{"dice", out}};
}
