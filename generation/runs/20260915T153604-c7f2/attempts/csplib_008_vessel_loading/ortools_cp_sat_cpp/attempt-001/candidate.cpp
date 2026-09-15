#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Vessel loading: lay rectangular containers out on the deck, each in one of
// its two orientations, keeping the required separation between classes.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int64_t deck_width = instance.at("deck_width").get<int64_t>();
  const int64_t deck_length = instance.at("deck_length").get<int64_t>();
  const int n_containers = instance.at("n_containers").get<int>();
  const std::vector<int64_t> width =
      instance.at("width").get<std::vector<int64_t>>();
  const std::vector<int64_t> length =
      instance.at("length").get<std::vector<int64_t>>();
  const std::vector<int64_t> classes =
      instance.at("classes").get<std::vector<int64_t>>();
  const std::vector<std::vector<int64_t>> separation =
      instance.at("separation").get<std::vector<std::vector<int64_t>>>();

  std::vector<IntVar> left;
  std::vector<IntVar> right;
  std::vector<IntVar> top;
  std::vector<IntVar> bottom;
  for (int i = 0; i < n_containers; ++i) {
    left.push_back(model.NewIntVar(Domain(0, deck_width)));
    right.push_back(model.NewIntVar(Domain(0, deck_width)));
    top.push_back(model.NewIntVar(Domain(0, deck_length)));
    bottom.push_back(model.NewIntVar(Domain(0, deck_length)));
  }

  // Each container sits either way round.
  for (int i = 0; i < n_containers; ++i) {
    BoolVar upright = model.NewBoolVar();
    model.AddEquality(right[i] - left[i], width[i]).OnlyEnforceIf(upright);
    model.AddEquality(top[i] - bottom[i], length[i]).OnlyEnforceIf(upright);
    model.AddEquality(right[i] - left[i], length[i]).OnlyEnforceIf(upright.Not());
    model.AddEquality(top[i] - bottom[i], width[i]).OnlyEnforceIf(upright.Not());
  }

  // No two containers overlap, and class pairs keep their separation.
  for (int x = 0; x < n_containers; ++x) {
    for (int y = x + 1; y < n_containers; ++y) {
      const int64_t sep =
          separation[classes[x] - 1][classes[y] - 1];
      BoolVar x_left = model.NewBoolVar();
      BoolVar x_right = model.NewBoolVar();
      BoolVar x_under = model.NewBoolVar();
      BoolVar x_above = model.NewBoolVar();
      model.AddLessOrEqual(right[x] + sep, left[y]).OnlyEnforceIf(x_left);
      model.AddGreaterOrEqual(left[x], right[y] + sep).OnlyEnforceIf(x_right);
      model.AddLessOrEqual(top[x] + sep, bottom[y]).OnlyEnforceIf(x_under);
      model.AddGreaterOrEqual(bottom[x], top[y] + sep).OnlyEnforceIf(x_above);
      model.AddBoolOr({x_left, x_right, x_under, x_above});
    }
  }

  json l = json::array();
  json r = json::array();
  json t = json::array();
  json b = json::array();
  for (int i = 0; i < n_containers; ++i) {
    l.push_back(left[i].index());
    r.push_back(right[i].index());
    t.push_back(top[i].index());
    b.push_back(bottom[i].index());
  }
  outputs = {{"left", l}, {"right", r}, {"top", t}, {"bottom", b}};
}
