// Devil's word: put a plus or minus sign before each integer so that the signed numbers sum to the total.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> arr = instance.at("arr").get<std::vector<int>>();
  int total = instance.at("total");
  int n = static_cast<int>(arr.size());

  // s[i] = 1 if the number arr[i] gets a plus sign, 0 if it gets a minus sign
  vec<IntVar*> s;
  createVars(s, n, 0, 1, true);

  // result[i] is arr[i] with its sign: result[i] = 2*arr[i]*s[i] - arr[i]
  vec<IntVar*> result;
  for (int i = 0; i < n; ++i) {
    IntVar* r = newIntVar(-arr[i], arr[i]);
    vec<int> coef;
    coef.push(1);
    coef.push(-2 * arr[i]);
    vec<IntVar*> vars;
    vars.push(r);
    vars.push(s[i]);
    int_linear(coef, vars, IRT_EQ, -arr[i]);
    result.push(r);
  }

  // the signed numbers sum to the target total
  int_linear(result, IRT_EQ, total);

  branch(s, VAR_INORDER, VAL_MIN);

  json out_arr = json::array();
  for (int i = 0; i < n; ++i) out_arr.push_back(dcp::out(result[i]));
  outputs = {{"result", out_arr}};
}
