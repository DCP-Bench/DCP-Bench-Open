#include <algorithm>
#include <cmath>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Travelling salesman: visit every location exactly once and return to the
// start, minimizing the total travelled distance, where the distance between
// two locations is their Euclidean distance rounded to an integer.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const json& locations = instance.at("locations");
  const int n = static_cast<int>(locations.size());

  // dist[i][j]: Euclidean distance rounded to the nearest integer, as the
  // reference computes it (a distance between integer points is never exactly
  // half-way between two integers, so the rounding rule does not matter).
  std::vector<std::vector<int64_t>> dist(n, std::vector<int64_t>(n, 0));
  int64_t total_bound = 0;
  for (int i = 0; i < n; ++i) {
    int64_t row_max = 0;
    for (int j = 0; j < n; ++j) {
      if (i == j) continue;
      const double dx = locations.at(i).at(0).get<double>() - locations.at(j).at(0).get<double>();
      const double dy = locations.at(i).at(1).get<double>() - locations.at(j).at(1).get<double>();
      dist[i][j] = std::llround(std::hypot(dx, dy));
      row_max = std::max(row_max, dist[i][j]);
    }
    total_bound += row_max;
  }

  // arc[i][j] is true when location j is visited immediately after location i.
  // The arcs chosen form a single tour through all locations (no self-loops, so
  // no location is skipped).
  CircuitConstraint circuit = model.AddCircuitConstraint();
  LinearExpr travelled;
  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) {
      if (i == j) continue;
      const BoolVar arc = model.NewBoolVar();
      circuit.AddArc(i, j, arc);
      travelled += dist[i][j] * arc;
    }
  }

  // travel_distance is the sum of the distances of the chosen arcs; its upper
  // bound is the sum, over locations, of the longest arc leaving each one.
  const IntVar travel_distance = model.NewIntVar(Domain(0, total_bound));
  model.AddEquality(travel_distance, travelled);

  // Minimize the travelled distance.
  model.Minimize(travel_distance);

  outputs = {{"travel_distance", travel_distance.index()}};
}
