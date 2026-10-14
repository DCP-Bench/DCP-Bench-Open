#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Best host: seat six guests around a round table so that every guest sits
// only next to the two people he or she is willing to sit beside.
// The problem has no instance data: guests and preferences are part of the puzzle.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int n = 6;
  const int Andrew = 0, Betty = 1, Cara = 2, Dave = 3, Erica = 4, Frank = 5;

  // prefs[g]: the two guests g will sit next to.
  const std::vector<std::vector<int>> prefs = {
      {Dave, Frank},    // Andrew
      {Cara, Erica},    // Betty
      {Betty, Frank},   // Cara
      {Andrew, Erica},  // Dave
      {Betty, Dave},    // Erica
      {Andrew, Cara},   // Frank
  };

  // x[i] is the guest in seat i; seats 0 and n-1 are also neighbours.
  std::vector<IntVar> x;
  for (int i = 0; i < n; ++i) x.push_back(model.NewIntVar(Domain(0, n - 1)));

  // Every guest has one seat.
  model.AddAllDifferent(x);

  // The pairs (guest, neighbour) where the guest accepts that neighbour.
  std::vector<std::vector<int64_t>> accepted;
  for (int g = 0; g < n; ++g)
    for (int p : prefs[g]) accepted.push_back({g, p});

  // The guest in each seat accepts both the left and the right neighbour.
  for (int i = 0; i < n; ++i) {
    for (int neighbour : {(i - 1 + n) % n, (i + 1) % n}) {
      TableConstraint ok = model.AddAllowedAssignments({x[i], x[neighbour]});
      for (const std::vector<int64_t>& pair : accepted) ok.AddTuple(pair);
    }
  }

  json out = json::array();
  for (const IntVar& v : x) out.push_back(v.index());
  outputs = {{"x", out}};
}
