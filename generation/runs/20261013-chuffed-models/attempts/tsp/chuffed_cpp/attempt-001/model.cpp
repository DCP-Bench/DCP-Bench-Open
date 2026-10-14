// Travelling salesman: find the shortest closed route that visits every city exactly once
// and returns to the start. Distances are Euclidean, rounded to the nearest integer.
#include "dcp.h"

#include <algorithm>
#include <cmath>
#include <numeric>
#include <vector>

void Build(const json& instance, json& outputs) {
  std::vector<std::vector<int>> loc = instance.at("locations").get<std::vector<std::vector<int>>>();
  int n = static_cast<int>(loc.size());  // number of cities

  // dist[i][j] is the Euclidean distance between cities i and j, rounded to an integer
  std::vector<std::vector<int>> dist(n, std::vector<int>(n, 0));
  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) {
      double dx = loc[i][0] - loc[j][0];
      double dy = loc[i][1] - loc[j][1];
      dist[i][j] = static_cast<int>(std::floor(std::sqrt(dx * dx + dy * dy) + 0.5));
    }
  }

  // succ[i] is the city visited right after city i; the successors form one tour
  vec<IntVar*> succ;
  createVars(succ, n, 0, n - 1);
  circuit(succ);

  // the cities other than i, nearest first; orders[i][k] is the k-th nearest city to i
  vec<vec<int>> orders;
  for (int i = 0; i < n; ++i) {
    std::vector<int> others;
    for (int j = 0; j < n; ++j) if (j != i) others.push_back(j);
    std::stable_sort(others.begin(), others.end(),
                     [&](int a, int b) { return dist[i][a] < dist[i][b]; });
    orders.push();
    for (int j : others) orders.last().push(j);
  }

  // rank[i] picks the successor of city i as its rank in orders[i], so the search tries the
  // nearest unvisited city first
  vec<IntVar*> rank;
  vec<IntVar*> leg;
  int max_leg = 0;
  for (int i = 0; i < n; ++i) {
    IntVar* r = newIntVar(0, n - 2);
    array_int_element(r, orders[i], succ[i]);
    rank.push(r);

    // leg[i] is the distance from city i to its successor; the cheapest leg from city i
    // is a lower bound on it
    vec<int> row;
    int row_max = 0;
    int row_min = 0;
    for (int j = 0; j < n; ++j) {
      row.push(dist[i][j]);
      row_max = std::max(row_max, dist[i][j]);
    }
    row_min = dist[i][orders[i][0]];
    max_leg += row_max;
    IntVar* d = newIntVar(row_min, row_max);
    array_int_element(succ[i], row, d);
    leg.push(d);
  }

  // the travel distance is the total of the legs of the tour
  IntVar* total = newIntVar(0, max_leg);
  vec<int> ones;
  for (int i = 0; i < n; ++i) ones.push(1);
  int_linear(ones, leg, IRT_EQ, total);

  // branch on the successors by rank, then minimize the travel distance
  branch(rank, VAR_INORDER, VAL_MIN);
  optimize(total, OPT_MIN);

  outputs = {{"travel_distance", dcp::out(total)}};
}
