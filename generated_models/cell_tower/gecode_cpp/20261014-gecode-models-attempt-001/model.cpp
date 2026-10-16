#include "dcp.h"

// Cell towers: choose which candidate sites get a tower so that the built towers
// stay within the budget and the covered population is as large as possible.
class CellTower : public dcp::Space {
 protected:
  BoolVarArray build;    // build[i] = 1 if a tower is built at site i
  BoolVarArray covered;  // covered[r] = 1 if region r is in range of a built tower
  IntVar total;          // total population covered

 public:
  explicit CellTower(const json& instance) {
    std::vector<int> cost = instance.at("cost").get<std::vector<int>>();
    std::vector<int> population = instance.at("population").get<std::vector<int>>();
    std::vector<std::vector<int>> delta = instance.at("delta").get<std::vector<std::vector<int>>>();
    int budget = instance.at("budget");

    int sites = static_cast<int>(cost.size());
    int regions = static_cast<int>(population.size());
    int totalPopulation = 0;
    for (int p : population) totalPopulation += p;

    build = BoolVarArray(*this, sites, 0, 1);
    covered = BoolVarArray(*this, regions, 0, 1);
    total = IntVar(*this, 0, totalPopulation);

    // a region can only be covered if a tower that reaches it is built
    for (int r = 0; r < regions; ++r) {
      BoolVarArgs vars;
      IntArgs coef;
      int reaching = 0;
      for (int i = 0; i < sites; ++i)
        if (delta[i][r] == 1) ++reaching;
      vars = BoolVarArgs(reaching + 1);
      coef = IntArgs(reaching + 1);
      int k = 0;
      for (int i = 0; i < sites; ++i) {
        if (delta[i][r] == 1) {
          vars[k] = build[i];
          coef[k] = 1;
          ++k;
        }
      }
      vars[k] = covered[r];
      coef[k] = -1;
      linear(*this, coef, vars, IRT_GQ, 0);
    }

    // the total cost of the built towers stays within the budget
    IntArgs costArgs(sites);
    for (int i = 0; i < sites; ++i) costArgs[i] = cost[i];
    BoolVarArgs buildArgs(sites);
    for (int i = 0; i < sites; ++i) buildArgs[i] = build[i];
    linear(*this, costArgs, buildArgs, IRT_LQ, budget);

    // total population covered is the sum of the populations of the covered regions
    IntArgs popArgs(regions);
    for (int r = 0; r < regions; ++r) popArgs[r] = population[r];
    BoolVarArgs coveredArgs(regions);
    for (int r = 0; r < regions; ++r) coveredArgs[r] = covered[r];
    linear(*this, popArgs, coveredArgs, IRT_EQ, total);

    branch(*this, build, BOOL_VAR_NONE(), BOOL_VAL_MAX());
    branch(*this, covered, BOOL_VAR_NONE(), BOOL_VAL_MAX());
    maximize(total);
    output("build_tower", build);
    output("total_population_covered", total);
  }

  CellTower(CellTower& s) : dcp::Space(s) {
    build.update(*this, s.build);
    covered.update(*this, s.covered);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new CellTower(*this); }
};

DCP_MODEL(CellTower)
