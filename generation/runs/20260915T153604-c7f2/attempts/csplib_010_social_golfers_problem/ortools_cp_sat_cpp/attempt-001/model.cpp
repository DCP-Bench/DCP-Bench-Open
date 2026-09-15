#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Social golfers: schedule weeks of play so every group is the right size and
// no two golfers are grouped together more than once.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n_weeks = instance.at("n_weeks").get<int>();
  const int n_groups = instance.at("n_groups").get<int>();
  const int group_size = instance.at("group_size").get<int>();
  const int n_golfers = n_groups * group_size;

  std::vector<std::vector<IntVar>> assign(n_golfers);
  for (int g = 0; g < n_golfers; ++g) {
    for (int w = 0; w < n_weeks; ++w) {
      assign[g].push_back(model.NewIntVar(Domain(0, n_groups - 1)));
    }
  }

  // in_group[g][w][gr] says golfer g is in group gr in week w.
  std::vector<std::vector<std::vector<BoolVar>>> in_group(
      n_golfers, std::vector<std::vector<BoolVar>>(n_weeks));
  for (int g = 0; g < n_golfers; ++g) {
    for (int w = 0; w < n_weeks; ++w) {
      for (int gr = 0; gr < n_groups; ++gr) {
        BoolVar here = model.NewBoolVar();
        model.AddEquality(assign[g][w], gr).OnlyEnforceIf(here);
        model.AddNotEqual(assign[g][w], gr).OnlyEnforceIf(here.Not());
        in_group[g][w].push_back(here);
      }
    }
  }

  // Every group in every week holds exactly group_size players.
  for (int gr = 0; gr < n_groups; ++gr) {
    for (int w = 0; w < n_weeks; ++w) {
      LinearExpr members;
      for (int g = 0; g < n_golfers; ++g) members += in_group[g][w][gr];
      model.AddEquality(members, group_size);
    }
  }

  // Any two golfers share a group in at most one week.
  for (int g1 = 0; g1 < n_golfers; ++g1) {
    for (int g2 = g1 + 1; g2 < n_golfers; ++g2) {
      LinearExpr meetings;
      for (int w = 0; w < n_weeks; ++w) {
        BoolVar together = model.NewBoolVar();
        model.AddEquality(assign[g1][w], assign[g2][w]).OnlyEnforceIf(together);
        model.AddNotEqual(assign[g1][w], assign[g2][w])
            .OnlyEnforceIf(together.Not());
        meetings += together;
      }
      model.AddLessOrEqual(meetings, 1);
    }
  }

  json out = json::array();
  for (int g = 0; g < n_golfers; ++g) {
    json row = json::array();
    for (int w = 0; w < n_weeks; ++w) row.push_back(assign[g][w].index());
    out.push_back(row);
  }
  outputs = {{"assign", out}};
}
