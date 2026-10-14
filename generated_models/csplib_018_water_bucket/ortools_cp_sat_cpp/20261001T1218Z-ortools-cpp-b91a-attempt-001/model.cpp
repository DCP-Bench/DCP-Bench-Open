#include <algorithm>
#include <set>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Water buckets (CSPLib 18): starting from a full large bucket and two empty
// smaller ones, reach the goal amounts with as few pourings as possible.
// A pouring empties the source bucket or fills the target bucket, whichever
// comes first. The plan is a fixed-length sequence of states; once the goal
// is reached, the remaining steps are padding states.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> capacities = instance.at("capacities").get<std::vector<int64_t>>();
  const std::vector<int64_t> initial_state =
      instance.at("initial_state").get<std::vector<int64_t>>();
  const std::vector<int64_t> goal_state = instance.at("goal_state").get<std::vector<int64_t>>();
  const int max_steps = instance.at("MAX_STEPS").get<int>();
  const int64_t pad = instance.at("PADDING_VALUE").get<int64_t>();
  const int nb = 3;  // three buckets
  const int64_t total_water = *std::max_element(initial_state.begin(), initial_state.end());

  // Every state (i, j, k) with all the water of the first bucket's capacity
  // shared out, k fitting in the third bucket, and every pouring between two
  // different buckets that moves a positive amount.
  std::set<std::vector<int64_t>> transitions;
  for (int64_t i = 0; i <= capacities[0]; ++i)
    for (int64_t j = 0; j <= capacities[1]; ++j) {
      const int64_t k = capacities[0] - i - j;
      if (k < 0 || k > capacities[2]) continue;
      const std::vector<int64_t> state = {i, j, k};
      for (int from = 0; from < nb; ++from)
        for (int to = 0; to < nb; ++to) {
          if (from == to) continue;
          const int64_t amount = std::min(state[from], capacities[to] - state[to]);
          if (amount <= 0) continue;
          std::vector<int64_t> next = state;
          next[from] -= amount;
          next[to] += amount;
          std::vector<int64_t> row = state;
          row.insert(row.end(), next.begin(), next.end());
          transitions.insert(row);
        }
    }

  // sequence[t][b]: water in bucket b at step t, or the padding value. The
  // domain runs from the padding value up to the total amount of water.
  std::vector<std::vector<IntVar>> sequence(max_steps);
  for (int t = 0; t < max_steps; ++t)
    for (int b = 0; b < nb; ++b) sequence[t].push_back(model.NewIntVar(Domain(pad, total_water)));

  // The sequence starts with the initial state.
  for (int b = 0; b < nb; ++b) model.AddEquality(sequence[0][b], initial_state[b]);

  // padded[t]: step t is padding (its first bucket holds the padding value).
  // at_goal[t]: step t is the goal state. Both are reified in both directions.
  std::vector<BoolVar> padded, at_goal;
  for (int t = 0; t < max_steps; ++t) {
    const BoolVar p = model.NewBoolVar();
    model.AddEquality(sequence[t][0], pad).OnlyEnforceIf(p);
    model.AddNotEqual(sequence[t][0], pad).OnlyEnforceIf(p.Not());
    padded.push_back(p);

    std::vector<BoolVar> same;
    for (int b = 0; b < nb; ++b) {
      const BoolVar eq = model.NewBoolVar();
      model.AddEquality(sequence[t][b], goal_state[b]).OnlyEnforceIf(eq);
      model.AddNotEqual(sequence[t][b], goal_state[b]).OnlyEnforceIf(eq.Not());
      same.push_back(eq);
    }
    const BoolVar g = model.NewBoolVar();
    model.AddBoolAnd(same).OnlyEnforceIf(g);
    std::vector<BoolVar> some_differs;
    for (const BoolVar& eq : same) some_differs.push_back(eq.Not());
    model.AddBoolOr(some_differs).OnlyEnforceIf(g.Not());
    at_goal.push_back(g);

    // A step that is not padding conserves the water and keeps every bucket
    // within its capacity.
    LinearExpr water;
    for (int b = 0; b < nb; ++b) {
      water += sequence[t][b];
      model.AddLinearConstraint(sequence[t][b], Domain(0, capacities[b]))
          .OnlyEnforceIf(p.Not());
    }
    model.AddEquality(water, total_water).OnlyEnforceIf(p.Not());
  }

  for (int t = 0; t + 1 < max_steps; ++t) {
    // After the goal, and after padding, the next step is all padding.
    for (int b = 0; b < nb; ++b) {
      model.AddEquality(sequence[t + 1][b], pad).OnlyEnforceIf(at_goal[t]);
      model.AddEquality(sequence[t + 1][b], pad).OnlyEnforceIf(padded[t]);
    }

    // Otherwise the next step is one valid pouring away from this one (a
    // pouring always changes the state). move[r] selects transition r; at
    // least one applies unless the step is the goal or padding.
    std::vector<BoolVar> options = {at_goal[t], padded[t]};
    for (const std::vector<int64_t>& row : transitions) {
      const BoolVar move = model.NewBoolVar();
      for (int b = 0; b < nb; ++b) {
        model.AddEquality(sequence[t][b], row[b]).OnlyEnforceIf(move);
        model.AddEquality(sequence[t + 1][b], row[nb + b]).OnlyEnforceIf(move);
      }
      options.push_back(move);
    }
    model.AddBoolOr(options);
  }

  // The goal is reached at some step.
  model.AddBoolOr(at_goal);

  // cost: the number of transfers, i.e. the number of non-padding steps minus one.
  LinearExpr steps;
  for (const BoolVar& p : padded) steps += p.Not();
  const IntVar cost = model.NewIntVar(Domain(0, max_steps - 1));
  model.AddEquality(cost, steps - 1);

  // Minimize the number of transfers.
  model.Minimize(cost);

  json seq = json::array();
  for (int t = 0; t < max_steps; ++t) {
    json row = json::array();
    for (int b = 0; b < nb; ++b) row.push_back(sequence[t][b].index());
    seq.push_back(row);
  }
  outputs = {{"cost", cost.index()}, {"sequence", seq}};
}
