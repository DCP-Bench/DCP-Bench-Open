#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Perfect square placement: tile a large square exactly with the given smaller
// squares, none of them overlapping or hanging over the edge.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int64_t base = instance.at("base").get<int64_t>();
  const std::vector<int64_t> sides =
      instance.at("sides").get<std::vector<int64_t>>();
  const int n = static_cast<int>(sides.size());

  std::vector<IntVar> x_coords;
  std::vector<IntVar> y_coords;
  for (int i = 0; i < n; ++i) {
    x_coords.push_back(model.NewIntVar(Domain(0, base)));
    y_coords.push_back(model.NewIntVar(Domain(0, base)));
    model.AddLessOrEqual(x_coords[i] + sides[i], base);
    model.AddLessOrEqual(y_coords[i] + sides[i], base);
  }

  for (int a = 0; a < n; ++a) {
    for (int b = a + 1; b < n; ++b) {
      BoolVar a_left = model.NewBoolVar();
      BoolVar b_left = model.NewBoolVar();
      BoolVar a_below = model.NewBoolVar();
      BoolVar b_below = model.NewBoolVar();
      model.AddLessOrEqual(x_coords[a] + sides[a], x_coords[b])
          .OnlyEnforceIf(a_left);
      model.AddLessOrEqual(x_coords[b] + sides[b], x_coords[a])
          .OnlyEnforceIf(b_left);
      model.AddLessOrEqual(y_coords[a] + sides[a], y_coords[b])
          .OnlyEnforceIf(a_below);
      model.AddLessOrEqual(y_coords[b] + sides[b], y_coords[a])
          .OnlyEnforceIf(b_below);
      model.AddBoolOr({a_left, b_left, a_below, b_below});
    }
  }

  json x_out = json::array();
  json y_out = json::array();
  for (int i = 0; i < n; ++i) {
    x_out.push_back(x_coords[i].index());
    y_out.push_back(y_coords[i].index());
  }
  outputs = {{"x_coords", x_out}, {"y_coords", y_out}};
}
