#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Frog circle: arrange the cards 1..n in a circle. The frog starts on card 1;
// from a card with value k it jumps k places clockwise. Find an arrangement
// in which the frog lands on every card.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();

  // x[p] is the card at position p of the circle.
  std::vector<IntVar> x;
  // pos[i] is the position the frog is on after i jumps.
  std::vector<IntVar> pos;
  // visited[i] is the card the frog is on after i jumps.
  std::vector<IntVar> visited;
  for (int i = 0; i < n; ++i) {
    x.push_back(model.NewIntVar(Domain(1, n)));
    pos.push_back(model.NewIntVar(Domain(0, n - 1)));
    visited.push_back(model.NewIntVar(Domain(1, n)));
  }

  // Each card appears once in the circle, the frog visits each position
  // once, and it visits each card once.
  model.AddAllDifferent(x);
  model.AddAllDifferent(pos);
  model.AddAllDifferent(visited);

  // The frog starts on card 1, at position 0.
  model.AddEquality(x[0], 1);
  model.AddEquality(pos[0], 0);
  model.AddEquality(visited[0], 1);

  // AddElement indexes an array of expressions, so convert x once.
  const std::vector<LinearExpr> x_exprs(x.begin(), x.end());

  for (int i = 1; i < n; ++i) {
    // The next position is the previous position plus the value of the card
    // there, wrapping around the circle. card_here is x[pos[i-1]].
    const IntVar card_here = model.NewIntVar(Domain(1, n));
    model.AddElement(pos[i - 1], x_exprs, card_here);
    const IntVar jump_target = model.NewIntVar(Domain(0, 2 * n - 1));
    model.AddEquality(jump_target, pos[i - 1] + card_here);
    model.AddModuloEquality(pos[i], jump_target, n);

    // The card visited at this step is the card at the new position.
    model.AddElement(pos[i], x_exprs, visited[i]);
  }

  json out = json::array();
  for (const IntVar& v : x) out.push_back(v.index());
  outputs = {{"x", out}};
}
