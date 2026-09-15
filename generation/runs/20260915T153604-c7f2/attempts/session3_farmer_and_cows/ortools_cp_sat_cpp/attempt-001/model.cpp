#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Farmer and cows: split the herd between the sons so that each gets his
// allotted number of cows and exactly the same amount of milk.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int num_cows = instance.at("num_cows").get<int>();
  const int num_sons = instance.at("num_sons").get<int>();
  const std::vector<int64_t> cows_per_son =
      instance.at("cows_per_son").get<std::vector<int64_t>>();

  // Cow i yields i + 1 units of milk, as the reference lays the herd out.
  int64_t total_milk = 0;
  std::vector<int64_t> milk_per_cow;
  for (int i = 0; i < num_cows; ++i) {
    milk_per_cow.push_back(i + 1);
    total_milk += i + 1;
  }
  const int64_t total_milk_per_son = total_milk / num_sons;

  std::vector<IntVar> cow_assignments;
  for (int i = 0; i < num_cows; ++i) {
    cow_assignments.push_back(model.NewIntVar(Domain(0, num_sons - 1)));
  }

  // One indicator per (cow, son) pair drives both the head count and the milk
  // total for that son.
  std::vector<std::vector<BoolVar>> to_son(num_cows);
  for (int i = 0; i < num_cows; ++i) {
    for (int son = 0; son < num_sons; ++son) {
      BoolVar gets = model.NewBoolVar();
      model.AddEquality(cow_assignments[i], son).OnlyEnforceIf(gets);
      model.AddNotEqual(cow_assignments[i], son).OnlyEnforceIf(gets.Not());
      to_son[i].push_back(gets);
    }
  }

  for (int son = 0; son < num_sons; ++son) {
    LinearExpr head_count;
    LinearExpr milk;
    for (int i = 0; i < num_cows; ++i) {
      head_count += to_son[i][son];
      milk += milk_per_cow[i] * to_son[i][son];
    }
    model.AddEquality(head_count, cows_per_son[son]);
    model.AddEquality(milk, total_milk_per_son);
  }

  json out = json::array();
  for (const IntVar& a : cow_assignments) out.push_back(a.index());
  outputs = {{"cow_assignments", out}};
}
