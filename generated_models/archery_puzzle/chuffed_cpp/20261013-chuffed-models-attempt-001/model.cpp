// Archery puzzle: the archer shoots any number of arrows at the rings of six targets,
// each arrow scoring one ring's value; find the total closest to the target score.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> targets = instance.at("targets").get<std::vector<int>>();
  int target = instance.at("target_score");
  int n = static_cast<int>(targets.size());

  // ring scores as coefficients of the total
  vec<int> score;
  for (int i = 0; i < n; ++i) score.push(targets[i]);

  // hits[i] = number of arrows that land on ring i; the total is at most twice the
  // target, since taking no arrows already gives a deviation of target
  vec<IntVar*> hits;
  for (int i = 0; i < n; ++i) {
    int maxh = (2 * target) / targets[i];
    IntVar* h = newIntVar(0, maxh);
    hits.push(h);
  }

  // total = sum of the ring scores of all arrows shot
  IntVar* total = newIntVar(0, 2 * target);
  int_linear(score, hits, IRT_EQ, total);

  // diff = total - target
  IntVar* diff = newIntVar(-target, 2 * target);
  vec<int> pm; pm.push(1); pm.push(-1);
  vec<IntVar*> td; td.push(total); td.push(diff);
  int_linear(pm, td, IRT_EQ, target);

  // deviation = |total - target|, the amount by which the score misses the target
  IntVar* dev = newIntVar(0, 2 * target);
  int_abs(diff, dev);

  // minimize the deviation from the target score
  branch(hits, VAR_INORDER, VAL_MIN);
  optimize(dev, OPT_MIN);

  json hs = json::array();
  for (int i = 0; i < n; ++i) hs.push_back(dcp::out(hits[i]));
  outputs = {{"hits", hs}};
}
