// Car sequencing: cars of different types are put in an assembly line so that
// no option station gets more cars than it can handle in any window of slots.
#include "dcp.h"

#include <algorithm>

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  // Data from the instance: car types, option capacities and option requirements.
  std::vector<int> demand = instance.at("demand").get<std::vector<int>>();
  std::vector<int> at_most = instance.at("at_most").get<std::vector<int>>();
  std::vector<int> per_slots = instance.at("per_slots").get<std::vector<int>>();
  std::vector<std::vector<int>> requires =
      instance.at("requires").get<std::vector<std::vector<int>>>();

  int types = static_cast<int>(demand.size());
  int options = static_cast<int>(at_most.size());
  int cars = 0;
  for (int d : demand) cars += d;

  // x[p][c] = 1 if the car in position p (0-based) is of type c.
  std::vector<std::vector<dcp::Lin>> x(cars, std::vector<dcp::Lin>(types));
  for (int p = 0; p < cars; ++p)
    for (int c = 0; c < types; ++c) x[p][c] = dcp::new_var(h, 0, 1);

  // each position holds exactly one car type
  for (int p = 0; p < cars; ++p) {
    dcp::Lin s = 0.0;
    for (int c = 0; c < types; ++c) s = s + x[p][c];
    dcp::add_row(h, s, 1, 1);
  }

  // each car type appears as many times as its demand
  for (int c = 0; c < types; ++c) {
    dcp::Lin s = 0.0;
    for (int p = 0; p < cars; ++p) s = s + x[p][c];
    dcp::add_row(h, s, demand[c], demand[c]);
  }

  // for each option, at most at_most cars needing it in any run of per_slots consecutive positions
  // (a run is cut to the line length when the line is shorter than per_slots)
  for (int o = 0; o < options; ++o) {
    int window = std::min(per_slots[o], cars);
    for (int start = 0; start + window <= cars; ++start) {
      dcp::Lin s = 0.0;
      for (int p = start; p < start + window; ++p)
        for (int c = 0; c < types; ++c)
          if (requires[c][o] == 1) s = s + x[p][c];
      dcp::add_row(h, s, -kHighsInf, at_most[o]);
    }
  }

  // output: the car type in each position, numbered from 0
  std::vector<dcp::Lin> sequence(cars);
  for (int p = 0; p < cars; ++p) {
    dcp::Lin t = 0.0;
    for (int c = 0; c < types; ++c) t = t + static_cast<double>(c) * x[p][c];
    sequence[p] = t;
  }
  out.add("sequence", sequence);
}
