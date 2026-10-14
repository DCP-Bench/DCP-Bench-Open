// Fifty puzzle: choose which dummies to knock over so that the numbers on them add up to exactly the target sum.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> values = instance.at("values").get<std::vector<int>>();
  int target = instance.at("target_sum");
  int num_dummies = static_cast<int>(values.size());

  // knocked[i] = 1 if dummy i is knocked over (each dummy falls at most once)
  vec<IntVar*> knocked;
  createVars(knocked, num_dummies, 0, 1, true);

  vec<int> coef;
  for (int i = 0; i < num_dummies; ++i) coef.push(values[i]);
  // the numbers on the dummies that are knocked over add up to exactly the target sum
  int_linear(coef, knocked, IRT_EQ, target);

  // decide dummy by dummy in the order given
  branch(knocked, VAR_INORDER, VAL_MAX);

  json dummies = json::array();
  for (int i = 0; i < num_dummies; ++i) dummies.push_back(dcp::out(knocked[i]));
  outputs = {{"dummies", dummies}};
}
