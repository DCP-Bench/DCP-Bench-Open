// Traffic lights: choose states for four vehicle lights V1..V4 and four pedestrian lights P1..P4 at a
// junction so that every consecutive (V_i, P_i, V_{i+1}, P_{i+1}) is one of the safe combinations.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<std::vector<int>> allowed = instance.at("allowed_tuples").get<std::vector<std::vector<int>>>();

  // vehicle light states: 0=red, 1=red-yellow, 2=green, 3=yellow
  vec<IntVar*> V;
  createVars(V, 4, 0, 3, true);
  // pedestrian light states: 0=red, 1=green
  vec<IntVar*> P;
  createVars(P, 4, 0, 1, true);

  vec<vec<int>> safe;
  for (const auto& tuple : allowed) {
    safe.push();
    for (int v : tuple) safe.last().push(v);
  }

  // for each i, (V_i, P_i, V_{i+1}, P_{i+1}) must be a safe combination (V_5 = V_1 and P_5 = P_1)
  for (int i = 0; i < 4; ++i) {
    vec<IntVar*> combo;
    combo.push(V[i]);
    combo.push(P[i]);
    combo.push(V[(i + 1) % 4]);
    combo.push(P[(i + 1) % 4]);
    table(combo, safe);
  }

  vec<IntVar*> lights;
  for (int i = 0; i < 4; ++i) lights.push(V[i]);
  for (int i = 0; i < 4; ++i) lights.push(P[i]);
  branch(lights, VAR_INORDER, VAL_MIN);

  json out = json::array();
  for (int i = 0; i < 8; ++i) out.push_back(dcp::out(lights[i]));
  outputs = {{"lights", out}};
}
