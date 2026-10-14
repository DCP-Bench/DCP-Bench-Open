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

  // Search heuristic: Chuffed can only try small values first, so branch on a rank variable
  // that maps to the car type. Types are ranked from most to least constrained: a type scores the
  // sum, over the options it requires, of how loaded that option's station is
  // (cars needing it per slot of capacity).
  std::vector<double> score(n_classes, 0.0);
  for (int j = 0; j < n_options; ++j) {
    double need = 0;
    for (int c = 0; c < n_classes; ++c) need += demand[c] * requires_[c][j];
    double load = need * per_slots[j] / (static_cast<double>(at_most[j]) * n_cars);
    for (int c = 0; c < n_classes; ++c) score[c] += requires_[c][j] * load;
  }
  std::vector<int> by_difficulty(n_classes);
  for (int c = 0; c < n_classes; ++c) by_difficulty[c] = c;
  std::stable_sort(by_difficulty.begin(), by_difficulty.end(),
                   [&](int x, int y) { return score[x] > score[y]; });
  vec<int> type_of_rank;
  for (int c = 0; c < n_classes; ++c) type_of_rank.push(by_difficulty[c]);
  vec<IntVar*> rank;
  createVars(rank, n_cars, 0, n_classes - 1);
  for (int i = 0; i < n_cars; ++i) array_int_element(rank[i], type_of_rank, sequence[i]);

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

    // Implied: the cars needing option j that are demanded must all fit. The last s positions
    // hold at least (total demand for option j) minus what the first n-s positions can take,
    // and the first n-s positions take at most at_most[j] per full window plus a partial window.
    int total_need = 0;
    for (int c = 0; c < n_classes; ++c) total_need += demand[c] * requires_[c][j];
    for (int s = 1; s < n_cars; ++s) {
      int prefix = n_cars - s;
      int cap = at_most[j] * (prefix / per_slots[j]) + std::min(at_most[j], prefix % per_slots[j]);
      int need_in_suffix = total_need - cap;
      if (need_in_suffix <= 0) continue;
      vec<IntVar*> suffix;
      for (int i = n_cars - s; i < n_cars; ++i) suffix.push(needs[i]);
      int_linear(suffix, IRT_GE, need_in_suffix);
    }
  }

  branch(rank, VAR_INORDER, VAL_MIN);

  json out = json::array();
  for (int i = 0; i < n_cars; ++i) out.push_back(dcp::out(sequence[i]));
  outputs = {{"sequence", out}};
}
