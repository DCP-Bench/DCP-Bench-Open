// Aircraft landing on one runway: choose a landing time for each aircraft in a fixed
// landing order, respecting its time window and the separation to every later aircraft,
// and minimise the total penalty for landing before or after the target time.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> earliest = instance.at("earliest_landing").get<std::vector<int>>();
  std::vector<int> latest = instance.at("latest_landing").get<std::vector<int>>();
  std::vector<int> target = instance.at("target_landing").get<std::vector<int>>();
  std::vector<int> penalty_after = instance.at("penalty_after").get<std::vector<int>>();
  std::vector<int> penalty_before = instance.at("penalty_before").get<std::vector<int>>();
  std::vector<std::vector<int>> separation =
      instance.at("separation_time").get<std::vector<std::vector<int>>>();
  int n = static_cast<int>(earliest.size());

  // land[i] is the landing time of aircraft i, inside its time window
  vec<IntVar*> land;
  for (int i = 0; i < n; ++i) land.push(newIntVar(earliest[i], latest[i]));

  // aircraft i lands before aircraft j when i < j, so they must be separated by separation_time[i][j]
  for (int i = 0; i < n; ++i) {
    for (int j = i + 1; j < n; ++j) {
      vec<int> coef;
      coef.push(-1);
      coef.push(1);
      vec<IntVar*> pair;
      pair.push(land[i]);
      pair.push(land[j]);
      int_linear(coef, pair, IRT_GE, separation[i][j]);
    }
  }

  // late[i] is at least how far after the target aircraft i lands (0 if not late)
  // early[i] is at least how far before the target aircraft i lands (0 if not early)
  // the penalties are positive, so the optimum sets each to its exact value
  vec<IntVar*> late, early;
  int upper = 0;
  for (int i = 0; i < n; ++i) {
    IntVar* l = newIntVar(0, latest[i] - target[i] > 0 ? latest[i] - target[i] : 0);
    IntVar* e = newIntVar(0, target[i] - earliest[i] > 0 ? target[i] - earliest[i] : 0);
    late.push(l);
    early.push(e);

    // landing minus target is at most late
    vec<int> c1;
    c1.push(1);
    c1.push(-1);
    vec<IntVar*> v1;
    v1.push(land[i]);
    v1.push(l);
    int_linear(c1, v1, IRT_LE, target[i]);

    // target minus landing is at most early
    vec<int> c2;
    c2.push(-1);
    c2.push(-1);
    vec<IntVar*> v2;
    v2.push(land[i]);
    v2.push(e);
    int_linear(c2, v2, IRT_LE, -target[i]);

    upper += penalty_after[i] * (latest[i] - target[i] > 0 ? latest[i] - target[i] : 0);
    upper += penalty_before[i] * (target[i] - earliest[i] > 0 ? target[i] - earliest[i] : 0);
  }

  // total penalty: penalty_after per unit of lateness and penalty_before per unit of earliness
  vec<int> coef;
  vec<IntVar*> terms;
  for (int i = 0; i < n; ++i) {
    coef.push(penalty_after[i]);
    terms.push(late[i]);
    coef.push(penalty_before[i]);
    terms.push(early[i]);
  }
  IntVar* total = newIntVar(0, upper);
  int_linear(coef, terms, IRT_EQ, total);

  // branch on the landing times, earliest first
  branch(land, VAR_INORDER, VAL_MIN);

  // minimise the total penalty
  optimize(total, OPT_MIN);

  json times = json::array();
  for (int i = 0; i < n; ++i) times.push_back(dcp::out(land[i]));
  outputs = {{"landing_times", times}, {"total_penalty", dcp::out(total)}};
}
