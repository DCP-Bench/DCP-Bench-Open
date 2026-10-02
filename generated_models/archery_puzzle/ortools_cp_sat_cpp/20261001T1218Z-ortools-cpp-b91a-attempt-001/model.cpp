#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Archery puzzle: choose how many arrows hit each target so that the total
// score gets as close as possible to the wanted score, with any number of arrows.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> targets =
      instance.at("targets").get<std::vector<int64_t>>();
  const int64_t target_score = instance.at("target_score").get<int64_t>();
  const int n = static_cast<int>(targets.size());

  // hits[i]: number of arrows that hit target i.  The reference caps it at
  // target_score; score and deviation are capped at twice target_score.
  std::vector<IntVar> hits;
  for (int i = 0; i < n; ++i) {
    hits.push_back(model.NewIntVar(Domain(0, target_score)));
  }
  IntVar score = model.NewIntVar(Domain(0, target_score * 2));
  IntVar deviation = model.NewIntVar(Domain(0, target_score * 2));

  // The score is the sum of the values of the targets that were hit.
  LinearExpr points;
  for (int i = 0; i < n; ++i) points += targets[i] * hits[i];
  model.AddEquality(score, points);

  // The deviation is the distance between the wanted score and the score.
  model.AddAbsEquality(deviation, LinearExpr(target_score) - score);

  // Come as close as possible to the wanted score.
  model.Minimize(deviation);

  json hits_out = json::array();
  for (const IntVar& h : hits) hits_out.push_back(h.index());
  outputs = {{"hits", hits_out}};
}
