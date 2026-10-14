#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Traffic lights: a four-way junction has four vehicle lights V1..V4 and four
// pedestrian lights P1..P4.  Choose a state for every light so that, for each
// pair of neighbouring roads, the combination (V_i, P_i, V_{i+1}, P_{i+1}) is
// one of the safe combinations, with road 5 being road 1.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<std::vector<int64_t>> allowed_tuples =
      instance.at("allowed_tuples").get<std::vector<std::vector<int64_t>>>();

  // Vehicle light states: 0 red, 1 red-yellow, 2 green, 3 yellow.
  // Pedestrian light states: 0 red, 1 green.  These ranges belong to the
  // problem statement, not to the instance.
  std::vector<IntVar> vehicle_lights, pedestrian_lights;
  for (int i = 0; i < 4; ++i) {
    vehicle_lights.push_back(model.NewIntVar(Domain(0, 3)));
  }
  for (int i = 0; i < 4; ++i) {
    pedestrian_lights.push_back(model.NewIntVar(Domain(0, 1)));
  }

  // Each pair of intersecting roads must show one of the allowed combinations
  // (V_i, P_i, V_{i+1}, P_{i+1}), with the roads wrapping around.
  for (int i = 0; i < 4; ++i) {
    const int next = (i + 1) % 4;
    TableConstraint safe = model.AddAllowedAssignments(
        {vehicle_lights[i], pedestrian_lights[i], vehicle_lights[next],
         pedestrian_lights[next]});
    for (const std::vector<int64_t>& tuple : allowed_tuples) {
      safe.AddTuple(tuple);
    }
  }

  // The lights in the order [V1, V2, V3, V4, P1, P2, P3, P4].
  json lights_out = json::array();
  for (const IntVar& v : vehicle_lights) lights_out.push_back(v.index());
  for (const IntVar& p : pedestrian_lights) lights_out.push_back(p.index());
  outputs = {{"lights", lights_out}};
}
