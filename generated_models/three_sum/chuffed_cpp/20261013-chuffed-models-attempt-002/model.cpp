// Three sum: select m of the given integers so that the selected integers sum to zero.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> nums = instance.at("nums").get<std::vector<int>>();
  int m = instance.at("m");
  int n = static_cast<int>(nums.size());

  // sel[i] = 1 if the integer nums[i] is selected
  vec<IntVar*> sel;
  createVars(sel, n, 0, 1, true);

  // exactly m integers are selected
  int_linear(sel, IRT_EQ, m);

  // the selected integers sum to zero
  vec<int> coef;
  for (int i = 0; i < n; ++i) coef.push(nums[i]);
  int_linear(coef, sel, IRT_EQ, 0);

  branch(sel, VAR_INORDER, VAL_MIN);

  json flags = json::array();
  for (int i = 0; i < n; ++i) flags.push_back(dcp::out(sel[i]));
  outputs = {{"indices", flags}};
}
