// Cell tower coverage: choose which sites get a tower, within the budget, to cover as much population as possible.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int budget = instance.at("budget");
  std::vector<int> cost = instance.at("cost").get<std::vector<int>>();
  std::vector<int> population = instance.at("population").get<std::vector<int>>();
  std::vector<std::vector<int>> delta = instance.at("delta").get<std::vector<std::vector<int>>>();
  int sites = static_cast<int>(cost.size());
  int regions = static_cast<int>(population.size());

  // build_tower[j] = 1 if a tower is built at site j
  vec<IntVar*> build_tower;
  createVars(build_tower, sites, 0, 1, true);

  // due to budget constraints, the total cost of the built towers must not exceed the budget
  vec<int> c;
  for (int j = 0; j < sites; ++j) c.push(cost[j]);
  int_linear(c, build_tower, IRT_LE, budget);

  // a region is covered if at least one built tower reaches it (delta[j][r] = 1 if site j covers region r)
  vec<IntVar*> covered;
  vec<int> pop;
  int total_pop = 0;
  for (int r = 0; r < regions; ++r) {
    vec<int> a;
    vec<IntVar*> reach;
    for (int j = 0; j < sites; ++j)
      if (delta[j][r]) {
        a.push(1);
        reach.push(build_tower[j]);
      }
    IntVar* cov = newIntVar(0, 1);
    if (reach.size() == 0) {
      int_rel(cov, IRT_EQ, 0);  // no site reaches this region
    } else {
      BoolView is_covered = newBoolVar();
      int_linear(a, reach, IRT_GE, 1, is_covered);
      bool2int(is_covered, cov);
    }
    covered.push(cov);
    pop.push(population[r]);
    total_pop += population[r];
  }

  // the total population covered is the sum of the populations of the covered regions
  IntVar* total_population_covered = newIntVar(0, total_pop);
  int_linear(pop, covered, IRT_EQ, total_population_covered);

  // cover as many people as possible
  branch(build_tower, VAR_INORDER, VAL_MAX);
  optimize(total_population_covered, OPT_MAX);

  json towers = json::array();
  for (int j = 0; j < sites; ++j) towers.push_back(dcp::out(build_tower[j]));
  outputs = {{"build_tower", towers}, {"total_population_covered", dcp::out(total_population_covered)}};
}
