#include "dcp.h"

#include <algorithm>
#include <cmath>
#include <vector>

// Travelling salesman problem: find a shortest closed tour that visits every city
// exactly once and returns to the origin city. The distance between two cities is
// their Euclidean distance rounded to an integer. Output the optimal travel distance.
class TSP : public dcp::Space {
 protected:
  IntVarArray succ;         // succ[i]: the city visited right after city i
  IntVar travel_distance;   // total length of the tour

 public:
  explicit TSP(const json& instance) {
    const auto& locations = instance.at("locations");
    int n = locations.size();
    std::vector<int> px(n), py(n);
    for (int i = 0; i < n; ++i) {
      px[i] = locations[i][0].get<int>();
      py[i] = locations[i][1].get<int>();
    }

    // distance between every pair of cities: Euclidean distance rounded to an integer
    IntArgs cost(n * n);
    long long bound = 0;
    for (int i = 0; i < n; ++i) {
      int row_max = 0;
      for (int j = 0; j < n; ++j) {
        double dx = px[i] - px[j], dy = py[i] - py[j];
        int d = static_cast<int>(std::lround(std::sqrt(dx * dx + dy * dy)));
        cost[i * n + j] = d;
        row_max = std::max(row_max, d);
      }
      bound += row_max;  // no tour can use more than the longest edge out of each city
    }

    // the tour: every city is followed by exactly one other city, and the successors
    // form a single cycle through all cities (no subtours)
    succ = IntVarArray(*this, n, 0, n - 1);
    travel_distance = IntVar(*this, 0, static_cast<int>(bound));
    circuit(*this, cost, succ, travel_distance);

    // branch on the successors; the tour length follows from them
    branch(*this, succ, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    // the tour should be as short as possible
    minimize(travel_distance);
    output("travel_distance", travel_distance);
  }

  TSP(TSP& s) : dcp::Space(s) {
    succ.update(*this, s.succ);
    travel_distance.update(*this, s.travel_distance);
  }
  Gecode::Space* copy() override { return new TSP(*this); }
};

DCP_MODEL(TSP)
