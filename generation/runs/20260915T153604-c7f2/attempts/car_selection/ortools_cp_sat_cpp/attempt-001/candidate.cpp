#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Car selection: match participants to cars they are interested in, at most
// one car each and one participant per car, maximizing the matches made.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<std::vector<int64_t>> possible =
      instance.at("possible_assignments")
          .get<std::vector<std::vector<int64_t>>>();
  const int num_participants = static_cast<int>(possible.size());
  const int num_cars =
      num_participants == 0 ? 0 : static_cast<int>(possible[0].size());

  std::vector<std::vector<BoolVar>> assign(num_participants);
  for (int i = 0; i < num_participants; ++i) {
    for (int j = 0; j < num_cars; ++j) {
      assign[i].push_back(model.NewBoolVar());
      // An assignment is only available where the participant is interested.
      model.AddLessOrEqual(assign[i][j], possible[i][j]);
    }
  }

  for (int i = 0; i < num_participants; ++i) {
    LinearExpr row;
    for (int j = 0; j < num_cars; ++j) row += assign[i][j];
    model.AddLessOrEqual(row, 1);
  }
  for (int j = 0; j < num_cars; ++j) {
    LinearExpr col;
    for (int i = 0; i < num_participants; ++i) col += assign[i][j];
    model.AddLessOrEqual(col, 1);
  }

  LinearExpr matched;
  for (int i = 0; i < num_participants; ++i) {
    for (int j = 0; j < num_cars; ++j) matched += assign[i][j];
  }
  model.Maximize(matched);

  json out = json::array();
  for (int i = 0; i < num_participants; ++i) {
    json row = json::array();
    for (int j = 0; j < num_cars; ++j) row.push_back(assign[i][j].index());
    out.push_back(row);
  }
  outputs = {{"assignments", out}};
}
