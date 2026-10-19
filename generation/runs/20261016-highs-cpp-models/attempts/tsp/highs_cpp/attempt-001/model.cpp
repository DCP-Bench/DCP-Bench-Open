// Travelling salesman problem: visit every city exactly once and return to the
// origin city (city 0), minimising the total length of the tour. The distance
// between two cities is the Euclidean distance between their points, rounded to
// an integer. Output travel_distance is the optimal tour length.
#include <cmath>
#include <vector>
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const auto& locs = instance.at("locations");
  const int n = static_cast<int>(locs.size());

  // distance between every pair of cities, rounded to an integer
  std::vector<std::vector<double>> dist(n, std::vector<double>(n, 0.0));
  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) {
      double dx = static_cast<double>(locs[i][0].get<int>()) - static_cast<double>(locs[j][0].get<int>());
      double dy = static_cast<double>(locs[i][1].get<int>()) - static_cast<double>(locs[j][1].get<int>());
      dist[i][j] = std::lround(std::sqrt(dx * dx + dy * dy));
    }
  }

  // x[i][j] = 1 when the tour goes directly from city i to city j (i != j)
  std::vector<std::vector<dcp::Lin>> x(n, std::vector<dcp::Lin>(n));
  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) {
      if (i != j) x[i][j] = dcp::new_var(h, 0, 1, true);
    }
  }

  // each city is left exactly once
  for (int i = 0; i < n; ++i) {
    dcp::Lin leave = 0;
    for (int j = 0; j < n; ++j) {
      if (i != j) leave = leave + x[i][j];
    }
    dcp::add_row(h, leave, 1, 1);
  }

  // each city is entered exactly once
  for (int j = 0; j < n; ++j) {
    dcp::Lin enter = 0;
    for (int i = 0; i < n; ++i) {
      if (i != j) enter = enter + x[i][j];
    }
    dcp::add_row(h, enter, 1, 1);
  }

  // the tour is a single cycle: position u[i] of city i in the tour, with the
  // origin city 0 at position 0 and every other city at a position 1..n-1
  std::vector<dcp::Lin> u(n);
  u[0] = dcp::new_var(h, 0, 0, true);
  for (int i = 1; i < n; ++i) {
    u[i] = dcp::new_var(h, 1, n - 1, true);
  }

  // if the tour goes from city i to city j (both not the origin), then u[j] is
  // after u[i]; the big-M n is the number of cities, which bounds the position gap
  for (int i = 1; i < n; ++i) {
    for (int j = 1; j < n; ++j) {
      if (i != j) {
        // u[i] - u[j] + n x[i][j] <= n - 1
        dcp::add_row(h, u[i] - u[j] + static_cast<double>(n) * x[i][j], -kHighsInf, n - 1);
      }
    }
  }

  // total length of the tour is the sum of the distances of the used edges
  dcp::Lin length = 0;
  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) {
      if (i != j) length = length + dist[i][j] * x[i][j];
    }
  }

  out.minimize(length);
  out.add("travel_distance", length);
}
