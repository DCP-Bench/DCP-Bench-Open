#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Finding celebrities: given who knows whom at a party, find the celebrities.
// A celebrity is known by everybody at the party and knows only other
// celebrities; at least one celebrity is present.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  // graph[i][j] == 1 when person i knows person j (the diagonal is part of the data).
  const std::vector<std::vector<int64_t>> graph =
      instance.at("graph").get<std::vector<std::vector<int64_t>>>();
  const int n = static_cast<int>(graph.size());

  // celebrities[i] is true when person i is a celebrity.
  std::vector<BoolVar> celebrities;
  for (int i = 0; i < n; ++i) celebrities.push_back(model.NewBoolVar());

  // num_celebrities counts the celebrities; at least one is present (domain 1..n).
  const IntVar num_celebrities = model.NewIntVar(Domain(1, n));
  LinearExpr celebrity_count;
  for (int i = 0; i < n; ++i) celebrity_count += celebrities[i];
  model.AddEquality(num_celebrities, celebrity_count);

  // Person i is a celebrity exactly when everybody knows i (the column of i
  // sums to n) and i knows as many people as there are celebrities (the row
  // of i sums to num_celebrities, which, with everybody knowing every
  // celebrity, means i knows only celebrities).
  // Both sums come from the data, so "known by everybody" is a constant per
  // person; only the comparison with num_celebrities depends on the search.
  for (int i = 0; i < n; ++i) {
    int64_t known_by = 0;  // how many people know i
    int64_t knows = 0;     // how many people i knows
    for (int j = 0; j < n; ++j) {
      known_by += graph[j][i];
      knows += graph[i][j];
    }
    if (known_by != n) {
      // Somebody does not know i, so i cannot be a celebrity.
      model.AddEquality(celebrities[i], 0);
    } else {
      // celebrities[i] <=> (num_celebrities == knows), posted in both directions.
      model.AddEquality(num_celebrities, knows).OnlyEnforceIf(celebrities[i]);
      model.AddNotEqual(num_celebrities, knows).OnlyEnforceIf(celebrities[i].Not());
    }
  }

  json out = json::array();
  for (const BoolVar& c : celebrities) out.push_back(c.index());
  outputs = {{"celebrities", out}};
}
