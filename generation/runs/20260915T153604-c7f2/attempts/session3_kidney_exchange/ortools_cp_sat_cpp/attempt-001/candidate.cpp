#include <set>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Kidney exchange: pair donors with compatible recipients so that anyone who
// gives also receives, nobody gives or receives twice, and as many transplants
// happen as possible.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int num_people = instance.at("num_people").get<int>();
  // compatible is ragged: one 1-based recipient list per donor.
  const json& compatible = instance.at("compatible");

  std::vector<std::set<int>> can_donate_to(num_people);
  for (int i = 0; i < num_people; ++i) {
    for (const auto& entry : compatible.at(i)) {
      can_donate_to[i].insert(entry.get<int>() - 1);
    }
  }

  std::vector<std::vector<BoolVar>> transplants(num_people);
  for (int i = 0; i < num_people; ++i) {
    for (int j = 0; j < num_people; ++j) {
      transplants[i].push_back(model.NewBoolVar());
      if (can_donate_to[i].count(j) == 0) {
        model.AddEquality(transplants[i][j], 0);
      }
    }
  }

  for (int i = 0; i < num_people; ++i) {
    LinearExpr gives;
    LinearExpr receives;
    for (int j = 0; j < num_people; ++j) {
      gives += transplants[i][j];
      receives += transplants[j][i];
    }
    // At most one donation out and one in.
    model.AddLessOrEqual(gives, 1);
    model.AddLessOrEqual(receives, 1);

    // Anyone who gives a kidney must also receive one.  With both sums capped
    // at one, that is exactly gives <= receives.
    model.AddLessOrEqual(gives, receives);
  }

  LinearExpr done;
  for (int i = 0; i < num_people; ++i) {
    for (int j = 0; j < num_people; ++j) done += transplants[i][j];
  }
  model.Maximize(done);

  json out = json::array();
  for (int i = 0; i < num_people; ++i) {
    json row = json::array();
    for (int j = 0; j < num_people; ++j) row.push_back(transplants[i][j].index());
    out.push_back(row);
  }
  outputs = {{"transplants", out}};
}
