// Car sequencing: cars of different types go down an assembly line. Each type needs a set of options, and each
// option station can handle at most at_most[o] cars in any window of per_slots[o] consecutive positions.
// Build a sequence of car types that uses each type exactly demand[t] times and respects every station's window.
#include "dcp.h"

#include <algorithm>

void Build(const json& instance, json& outputs) {
  auto demand = instance.at("demand").get<std::vector<int>>();
  auto requires_ = instance.at("requires").get<std::vector<std::vector<int>>>();
  auto at_most = instance.at("at_most").get<std::vector<int>>();
  auto per_slots = instance.at("per_slots").get<std::vector<int>>();

  int types = static_cast<int>(demand.size());
  int options = static_cast<int>(at_most.size());
  int cars = 0;
  for (int d : demand) cars += d;

  // type[p] is the car type at position p of the assembly line (0-based)
  vec<IntVar*> type;
  createVars(type, cars, 0, types - 1, true);

  // each car type t appears exactly demand[t] times in the sequence
  for (int t = 0; t < types; ++t) {
    vec<BoolView> at_t;
    for (int p = 0; p < cars; ++p) {
      BoolView b = newBoolVar();
      int_rel_reif(type[p], IRT_EQ, t, b);
      at_t.push(b);
    }
    bool_linear(at_t, IRT_EQ, getConstant(demand[t]));
  }

  // uses[o][p] is 1 when the car at position p needs option o (from the requires table of its type)
  std::vector<vec<IntVar*>> uses(options);
  for (int o = 0; o < options; ++o) {
    vec<int> needs;
    for (int t = 0; t < types; ++t) needs.push(requires_[t][o]);
    for (int p = 0; p < cars; ++p) {
      IntVar* u = newIntVar(0, 1);
      array_int_element(type[p], needs, u);
      uses[o].push(u);
    }
  }

  // every window of per_slots[o] consecutive positions has at most at_most[o] cars that need option o
  for (int o = 0; o < options; ++o) {
    for (int start = 0; start + per_slots[o] <= cars; ++start) {
      vec<IntVar*> window;
      for (int p = start; p < start + per_slots[o]; ++p) window.push(uses[o][p]);
      int_linear(window, IRT_LE, at_most[o]);
    }
  }

  // redundant: the stations' window limits cap the cars that need option o in any prefix or suffix of the line, and the
  // total demand for the option is known, so the opposite end must hold the rest (implied by windows and demand)
  for (int o = 0; o < options; ++o) {
    int total_o = 0;
    for (int t = 0; t < types; ++t) total_o += demand[t] * requires_[t][o];
    auto cap = [&](int m) { return at_most[o] * (m / per_slots[o]) + std::min(at_most[o], m % per_slots[o]); };
    for (int p = 1; p < cars; ++p) {
      vec<IntVar*> prefix, suffix;
      for (int q = 0; q < p; ++q) prefix.push(uses[o][q]);
      for (int q = p; q < cars; ++q) suffix.push(uses[o][q]);
      int_linear(prefix, IRT_LE, cap(p));
      int_linear(suffix, IRT_LE, cap(cars - p));
      if (total_o - cap(p) > 0) int_linear(suffix, IRT_GE, total_o - cap(p));
      if (total_o - cap(cars - p) > 0) int_linear(prefix, IRT_GE, total_o - cap(cars - p));
    }
  }

  // search heuristic: try the car types that need the most heavily loaded options first. rank[p] is the position
  // of the car type at p in a list of types sorted by that load; branching on rank (smallest first) tries the
  // most constrained type first
  std::vector<double> load(options, 0.0);
  for (int o = 0; o < options; ++o) {
    int total_o = 0;
    for (int t = 0; t < types; ++t) total_o += demand[t] * requires_[t][o];
    load[o] = static_cast<double>(total_o) * per_slots[o] / (static_cast<double>(at_most[o]) * cars);
  }
  std::vector<double> score(types, 0.0);
  for (int t = 0; t < types; ++t)
    for (int o = 0; o < options; ++o)
      if (requires_[t][o]) score[t] += load[o] * load[o];
  std::vector<int> by_load(types);
  for (int t = 0; t < types; ++t) by_load[t] = t;
  std::stable_sort(by_load.begin(), by_load.end(), [&](int x, int y) { return score[x] > score[y]; });
  vec<int> order;
  for (int t = 0; t < types; ++t) order.push(by_load[t]);
  vec<IntVar*> rank;
  createVars(rank, cars, 0, types - 1, true);
  for (int p = 0; p < cars; ++p) array_int_element(rank[p], order, type[p]);
  branch(rank, VAR_INORDER, VAL_MIN);
  // Luby restarts and alternating with VSIDS (both off by default in Chuffed) remove the heavy tail of the search
  so.restart_type = LUBY;
  so.restart_scale = 600;
  so.toggle_vsids = true;

  outputs = json::array();
  json seq = json::array();
  for (int p = 0; p < cars; ++p) seq.push_back(dcp::out(type[p]));
  outputs = {{"sequence", seq}};
}
