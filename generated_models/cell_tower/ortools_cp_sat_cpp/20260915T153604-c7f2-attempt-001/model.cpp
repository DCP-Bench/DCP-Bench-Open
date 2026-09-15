#include <numeric>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Cell tower siting: build towers within budget so as to cover the largest
// population.  A region counts as covered only if some built site reaches it.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<std::vector<int64_t>> delta =
      instance.at("delta").get<std::vector<std::vector<int64_t>>>();
  const std::vector<int64_t> cost =
      instance.at("cost").get<std::vector<int64_t>>();
  const std::vector<int64_t> population =
      instance.at("population").get<std::vector<int64_t>>();
  const int64_t budget = instance.at("budget").get<int64_t>();
  const int num_sites = static_cast<int>(cost.size());
  const int num_regions = static_cast<int>(population.size());

  std::vector<BoolVar> build_tower;
  for (int i = 0; i < num_sites; ++i) build_tower.push_back(model.NewBoolVar());
  std::vector<BoolVar> covered;
  for (int j = 0; j < num_regions; ++j) covered.push_back(model.NewBoolVar());

  for (int j = 0; j < num_regions; ++j) {
    LinearExpr reach;
    for (int i = 0; i < num_sites; ++i) reach += delta[i][j] * build_tower[i];
    model.AddLessOrEqual(covered[j], reach);
  }

  LinearExpr spend;
  for (int i = 0; i < num_sites; ++i) spend += cost[i] * build_tower[i];
  model.AddLessOrEqual(spend, budget);

  LinearExpr reached;
  for (int j = 0; j < num_regions; ++j) reached += population[j] * covered[j];
  const int64_t population_total =
      std::accumulate(population.begin(), population.end(), int64_t{0});
  IntVar total_covered = model.NewIntVar(Domain(0, population_total));
  model.AddEquality(total_covered, reached);
  model.Maximize(total_covered);

  json towers = json::array();
  for (const BoolVar& b : build_tower) towers.push_back(b.index());
  outputs = {{"build_tower", towers},
             {"total_population_covered", total_covered.index()}};
}
