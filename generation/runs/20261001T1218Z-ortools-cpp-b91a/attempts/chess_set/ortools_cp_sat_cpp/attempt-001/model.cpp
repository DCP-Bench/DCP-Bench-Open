#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Chess sets: a joinery makes small and large boxwood chess sets with limited
// lathe hours and boxwood per week; decide how many of each to make to
// maximize weekly profit.
// The problem has no instance data: all resource figures are part of the puzzle.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const IntVar small_set = model.NewIntVar(Domain(0, 100));
  const IntVar large_set = model.NewIntVar(Domain(0, 100));
  const IntVar max_profit = model.NewIntVar(Domain(0, 10000));

  // Boxwood: 1 kg per small set, 3 kg per large set, 200 kg per week.
  model.AddLessOrEqual(small_set + 3 * large_set, 200);

  // Lathe hours: 3 per small set, 2 per large set, 160 per week.
  model.AddLessOrEqual(3 * small_set + 2 * large_set, 160);

  // Profit: $5 per small set and $20 per large set.
  model.AddEquality(max_profit, 5 * small_set + 20 * large_set);

  // Maximize the profit.
  model.Maximize(max_profit);

  outputs = {{"small_set", small_set.index()},
             {"large_set", large_set.index()},
             {"max_profit", max_profit.index()}};
}
