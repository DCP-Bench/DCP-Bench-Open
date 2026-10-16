// Cell tower coverage: choose which candidate sites get a tower so that the
// total build cost stays within the budget and the covered population is maximal.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  // the number of sites and regions, and all data, are read from this instance
  std::vector<int> cost = instance.at("cost").get<std::vector<int>>();
  std::vector<int> population = instance.at("population").get<std::vector<int>>();
  std::vector<std::vector<int>> delta = instance.at("delta").get<std::vector<std::vector<int>>>();
  int budget = instance.at("budget").get<int>();
  int sites = static_cast<int>(cost.size());
  int regions = static_cast<int>(population.size());

  // build_tower[s] = 1 if a tower is built at candidate site s
  std::vector<dcp::Lin> build_tower;
  for (int s = 0; s < sites; ++s) build_tower.push_back(dcp::new_var(h, 0, 1));

  // covered[r] = 1 if region r is covered by a built tower (auxiliary)
  std::vector<dcp::Lin> covered;
  for (int r = 0; r < regions; ++r) covered.push_back(dcp::new_var(h, 0, 1));

  // the total cost of the towers built must not exceed the budget
  dcp::Lin total_cost = 0;
  for (int s = 0; s < sites; ++s) total_cost = total_cost + cost[s] * build_tower[s];
  dcp::add_row(h, total_cost, -kHighsInf, budget);

  // a region counts as covered only if some built tower reaches it
  // (covered[r] <= sum of the towers whose site covers region r)
  for (int r = 0; r < regions; ++r) {
    dcp::Lin reach = 0;
    for (int s = 0; s < sites; ++s) reach = reach + delta[s][r] * build_tower[s];
    dcp::add_row(h, reach - covered[r], 0, kHighsInf);
  }

  // the population covered is the sum of the populations of the covered regions
  dcp::Lin total_population = 0;
  for (int r = 0; r < regions; ++r) total_population = total_population + population[r] * covered[r];

  out.add("build_tower", build_tower);
  out.add("total_population_covered", total_population);
  out.maximize(total_population);
}
