#include <utility>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Football transfers: buy players with a GBP 30 million limit, spending as close
// to it as possible without going over: exactly one goalkeeper, at least two
// defenders, three midfielders and two strikers, and at least eleven players.
// The problem has no instance data. The prices, quotas and budget below are the
// statement's, in GBP thousands so they are integers.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int budget = 30000;
  // Prices per position: goalkeepers, defenders, midfielders, strikers.
  const std::vector<std::vector<int>> costs = {
      {730, 1280, 3880},
      {920, 1310, 1620, 2410, 2790, 3280, 3910, 4570},
      {1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130},
      {4460, 6470, 7780, 8390, 9500}};
  // Minimum and maximum number bought per position.
  const std::vector<std::pair<int, int>> min_max = {{1, 1}, {2, 10}, {3, 10}, {2, 10}};

  LinearExpr total_cost;
  LinearExpr total_players;
  for (size_t i = 0; i < costs.size(); ++i) {
    LinearExpr bought;  // players bought in position i
    for (int cost : costs[i]) {
      const BoolVar buy = model.NewBoolVar();  // whether this player is bought
      bought += buy;
      total_cost += cost * buy;
    }
    // Each position has its own quota.
    model.AddLinearConstraint(bought, Domain(min_max[i].first, min_max[i].second));
    total_players += bought;
  }

  // At least eleven players in total.
  model.AddGreaterOrEqual(total_players, 11);

  // z is the total price, which must stay within the budget and is maximised.
  const IntVar z = model.NewIntVar(Domain(0, budget));
  model.AddEquality(z, total_cost);
  model.Maximize(z);

  outputs = {{"z", z.index()}};
}
