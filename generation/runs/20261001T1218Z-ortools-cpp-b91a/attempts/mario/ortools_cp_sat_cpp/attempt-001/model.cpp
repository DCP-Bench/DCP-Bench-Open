#include <numeric>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Mario: Mario starts at his house and ends at Luigi's house, collecting the
// gold of every house he visits. Travelling between houses burns fuel and
// Mario has a limited amount. Choose the route that collects the most gold
// within the fuel limit. The route is reported as a successor for every house
// (s[i] == i when house i is not on the route, and Luigi's successor is
// Mario's house, which closes the route into a loop).
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n_houses = instance.at("nHouses").get<int>();
  const int mario = instance.at("marioHouse").get<int>();
  const int luigi = instance.at("luigiHouse").get<int>();
  const int64_t fuel_limit = instance.at("fuelLimit").get<int64_t>();
  // arc_fuel[i][j] is the fuel needed to go from house i to house j.
  const std::vector<std::vector<int64_t>> arc_fuel =
      instance.at("arc_fuel").get<std::vector<std::vector<int64_t>>>();
  const std::vector<int64_t> gold_in_house =
      instance.at("goldInHouse").get<std::vector<int64_t>>();

  // Which successors a house may have: Mario's and Luigi's houses are always
  // on the route, so they cannot skip themselves (no self-loop), and Luigi's
  // successor is Mario's house. Every other house may follow any other house
  // or skip itself (successor = itself).
  auto may_follow = [&](int i, int j) {
    if (i == j && (i == mario || i == luigi)) return false;
    if (i == luigi && j != mario) return false;
    return true;
  };

  // s[i] is the house that follows house i, or i itself when house i is not visited.
  std::vector<IntVar> s;
  for (int i = 0; i < n_houses; ++i) {
    std::vector<int64_t> successors;
    for (int j = 0; j < n_houses; ++j)
      if (may_follow(i, j)) successors.push_back(j);
    s.push_back(model.NewIntVar(Domain::FromValues(successors)));
  }

  // The visited houses form one loop (Mario ... Luigi, back to Mario) and the
  // others stay out of it. The reference gets this from an all-different
  // successor array plus a rank per house that stops separate sub-loops; the
  // circuit constraint states it directly. An arc (i, j) is used when house j
  // follows house i; a self-loop (i, i) means house i is skipped.
  CircuitConstraint route = model.AddCircuitConstraint();
  LinearExpr fuel_used;       // fuel burnt on the arcs that are used
  LinearExpr gold_collected;  // gold of every visited house
  for (int i = 0; i < n_houses; ++i) {
    for (int j = 0; j < n_houses; ++j) {
      if (!may_follow(i, j)) continue;
      const BoolVar uses_arc = model.NewBoolVar();
      route.AddArc(i, j, uses_arc);
      // Exactly one outgoing arc of house i is used (circuit property), and
      // then s[i] is the head of that arc.
      model.AddEquality(s[i], j).OnlyEnforceIf(uses_arc);
      fuel_used += arc_fuel[i][j] * uses_arc;
      // House i is visited when its arc leads elsewhere; then its gold counts.
      if (i != j) gold_collected += gold_in_house[i] * uses_arc;
    }
  }

  // Mario does not use more fuel than he has.
  model.AddLessOrEqual(fuel_used, fuel_limit);

  // Maximize the gold collected on the visited houses.
  const int64_t gold_bound = std::accumulate(gold_in_house.begin(), gold_in_house.end(), int64_t{0});
  const IntVar gold = model.NewIntVar(Domain(0, gold_bound));
  model.AddEquality(gold, gold_collected);
  model.Maximize(gold);

  json out = json::array();
  for (const IntVar& v : s) out.push_back(v.index());
  outputs = {{"s", out}};
}
