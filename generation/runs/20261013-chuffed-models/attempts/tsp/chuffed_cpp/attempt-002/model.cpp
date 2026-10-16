// Travelling salesman problem: a shortest closed tour visits every city exactly once and returns to the origin.
// Distance between two cities is the Euclidean distance between their points, rounded to an integer.
#include "dcp.h"

#include <cmath>
#include <limits>

void Build(const json& instance, json& outputs) {
  auto loc = instance.at("locations").get<std::vector<std::vector<int>>>();
  int n = static_cast<int>(loc.size());

  // dist[i][j] is the Euclidean distance between cities i and j, rounded to an integer
  std::vector<std::vector<int>> dist(n, std::vector<int>(n, 0));
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) {
      double dx = loc[i][0] - loc[j][0], dy = loc[i][1] - loc[j][1];
      dist[i][j] = static_cast<int>(std::lround(std::sqrt(dx * dx + dy * dy)));
    }

  // succ[i] is the city visited directly after city i; the successors form one tour through all cities
  vec<IntVar*> succ;
  createVars(succ, n, 0, n - 1);
  for (int i = 0; i < n; ++i) int_rel(succ[i], IRT_NE, i);
  circuit(succ);

  // leg[i] is the length of the leg leaving city i, looked up from the distance row of i
  vec<IntVar*> leg;
  vec<int> ones;
  int total_max = 0;
  for (int i = 0; i < n; ++i) {
    int mind = std::numeric_limits<int>::max(), maxd = 0;
    vec<int> row;
    for (int j = 0; j < n; ++j) {
      row.push(dist[i][j]);
      if (j != i) { mind = std::min(mind, dist[i][j]); maxd = std::max(maxd, dist[i][j]); }
    }
    total_max += maxd;
    IntVar* li = newIntVar(mind, maxd);
    array_int_element(succ[i], row, li);
    // every leg is at least the shortest distance from its city
    int_rel(li, IRT_GE, mind);
    leg.push(li);
    ones.push(1);
  }

  // travel_distance is the total length of the tour
  IntVar* total = newIntVar(0, total_max);
  int_linear(ones, leg, IRT_EQ, total);

  // branch on the objective first, then on the successors
  vec<IntVar*> objv;
  objv.push(total);
  branch(objv, VAR_INORDER, VAL_MIN);
  branch(succ, VAR_ACTIVITY, VAL_MIN);
  optimize(total, OPT_MIN);

  outputs = {{"travel_distance", dcp::out(total)}};
}
