#include <algorithm>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Set card game: among the cards on the table, pick three that form a "set":
// for each of the four features (number, fill, colour, shape) the three cards
// show either all the same value or three different values.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  // cards_data[c] = [number, fill, colour, shape] of card c.
  const json& cards = instance.at("cards_data");
  const int n_cards = static_cast<int>(cards.size());
  const int n_features = 4;

  // winning[k] is the 0-based index of the k-th chosen card.
  std::vector<IntVar> winning;
  for (int k = 0; k < 3; ++k) winning.push_back(model.NewIntVar(Domain(0, n_cards - 1)));

  // The three chosen cards are different cards.
  model.AddAllDifferent(winning);

  for (int f = 0; f < n_features; ++f) {
    // Column f of the card table: the value of feature f on every card.
    std::vector<int64_t> column;
    for (int c = 0; c < n_cards; ++c) column.push_back(cards.at(c).at(f).get<int64_t>());
    const int64_t lo = *std::min_element(column.begin(), column.end());
    const int64_t hi = *std::max_element(column.begin(), column.end());

    // v[k] is the value of feature f on the k-th chosen card.
    std::vector<IntVar> v;
    for (int k = 0; k < 3; ++k) {
      const IntVar value = model.NewIntVar(Domain(lo, hi));
      model.AddElement(winning[k], column, value);
      v.push_back(value);
    }

    // The feature is all equal on the three cards, or all different.
    const BoolVar all_equal = model.NewBoolVar();
    model.AddEquality(v[0], v[1]).OnlyEnforceIf(all_equal);
    model.AddEquality(v[1], v[2]).OnlyEnforceIf(all_equal);
    const BoolVar all_different = model.NewBoolVar();
    model.AddNotEqual(v[0], v[1]).OnlyEnforceIf(all_different);
    model.AddNotEqual(v[1], v[2]).OnlyEnforceIf(all_different);
    model.AddNotEqual(v[0], v[2]).OnlyEnforceIf(all_different);
    model.AddBoolOr({all_equal, all_different});
  }

  json out = json::array();
  for (const IntVar& w : winning) out.push_back(w.index());
  outputs = {{"winning_cards", out}};
}
