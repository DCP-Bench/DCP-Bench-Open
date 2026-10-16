// Bales of hay: recover n bale weights from the multiset of their pairwise sums.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");
  std::vector<int> sums = instance.at("weights").get<std::vector<int>>();
  int m = static_cast<int>(sums.size());  // number of pairwise sums, n*(n-1)/2

  // the largest sum is the largest pair of bales; bales are weights, so a bale
  // weighs at most the largest sum and at least minus that (a generous bound)
  int big = 0;
  for (int s : sums) big = std::max(big, std::abs(s));

  // bale[i] = weight of bale i
  vec<IntVar*> bale;
  createVars(bale, n, -big, big);

  vec<int> table;
  for (int s : sums) table.push(s);

  // every pair of bales gives one weighed sum; the sums are assigned to the
  // listed weights so that each listed weight is used exactly once
  vec<IntVar*> slot;
  for (int i = 0; i < n; ++i) {
    for (int j = i + 1; j < n; ++j) {
      // the weight of the pair (bale i, bale j) is the sum of the two bales
      IntVar* pair = newIntVar(-2 * big, 2 * big);
      vec<int> c;
      c.push(1); c.push(1);
      vec<IntVar*> two;
      two.push(bale[i]);
      two.push(bale[j]);
      int_linear(c, two, IRT_EQ, pair);

      // the position of this pair in the sorted list of weights
      IntVar* pos = newIntVar(0, m - 1);
      slot.push(pos);

      // the pair weight equals the listed weight at its position
      array_int_element(pos, table, pair, 0);
    }
  }

  // each listed weight is matched by exactly one pair of bales
  all_different(slot);

  // the bale weights are the unknowns to search over
  branch(bale, VAR_INORDER, VAL_MIN);

  json weights = json::array();
  for (int i = 0; i < n; ++i) weights.push_back(dcp::out(bale[i]));
  outputs = {{"bales", weights}};
}
