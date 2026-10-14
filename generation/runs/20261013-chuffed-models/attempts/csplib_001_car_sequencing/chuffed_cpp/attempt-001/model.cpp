// Car sequencing: order the cars on an assembly line so that no option station is overloaded.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> at_most = instance.at("at_most").get<std::vector<int>>();
  std::vector<int> per_slots = instance.at("per_slots").get<std::vector<int>>();
  std::vector<int> demand = instance.at("demand").get<std::vector<int>>();
  std::vector<std::vector<int>> requires_ = instance.at("requires").get<std::vector<std::vector<int>>>();
  int n_classes = static_cast<int>(demand.size());
  int n_options = static_cast<int>(at_most.size());
  int n_cars = 0;
  for (int d : demand) n_cars += d;  // the line holds exactly the cars to be produced

  // sequence[i] is the car type at position i of the assembly line
  vec<IntVar*> sequence;
  createVars(sequence, n_cars, 0, n_classes - 1, true);

  // every car type is produced exactly as often as demanded
  for (int c = 0; c < n_classes; ++c) {
    vec<BoolView> is_c;
    for (int i = 0; i < n_cars; ++i) {
      BoolView b = newBoolVar();
      int_rel_reif(sequence[i], IRT_EQ, c, b);
      is_c.push(b);
    }
    IntVar* demanded = getConstant(demand[c]);
    bool_linear(is_c, IRT_EQ, demanded);
  }

  // needs[j][i] = 1 if the car at position i requires option j
  for (int j = 0; j < n_options; ++j) {
    vec<int> col;
    for (int c = 0; c < n_classes; ++c) col.push(requires_[c][j]);
    vec<IntVar*> needs;
    createVars(needs, n_cars, 0, 1, true);
    for (int i = 0; i < n_cars; ++i) array_int_element(sequence[i], col, needs[i]);

    // the station for option j handles at most at_most[j] cars in any window of per_slots[j] consecutive cars
    for (int s = 0; s + per_slots[j] <= n_cars; ++s) {
      vec<IntVar*> window;
      for (int k = 0; k < per_slots[j]; ++k) window.push(needs[s + k]);
      int_linear(window, IRT_LE, at_most[j]);
    }
  }

  branch(sequence, VAR_INORDER, VAL_MIN);

  json out = json::array();
  for (int i = 0; i < n_cars; ++i) out.push_back(dcp::out(sequence[i]));
  outputs = {{"sequence", out}};
}
