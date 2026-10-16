// Just forgotten: find an account number that uses each digit 0 .. n-1 exactly once, given several
// sets of digits in which exactly k digits are in the same position as in the account number.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<std::vector<int>> sets = instance.at("sets").get<std::vector<std::vector<int>>>();
  int k = instance.at("num_correct_digits");
  int n = static_cast<int>(sets[0].size());

  // x[i] is the digit at position i of the account number
  vec<IntVar*> x;
  createVars(x, n, 0, n - 1, true);

  // the account number has all the digits from 0 to n-1, each once
  all_different(x);

  // for each set, exactly k of its digits sit in the same position as in the account number
  for (int s = 0; s < static_cast<int>(sets.size()); ++s) {
    // same[i] is true when the account number and this set agree at position i
    vec<BoolView> same;
    for (int i = 0; i < n; ++i) {
      BoolView b = newBoolVar();
      int_rel_reif(x[i], IRT_EQ, sets[s][i], b);
      same.push(b);
    }

    // exactly k positions agree
    bool_linear(same, IRT_EQ, getConstant(k));
  }

  // decide the digits in position order
  branch(x, VAR_INORDER, VAL_MIN);

  json arr = json::array();
  for (int i = 0; i < n; ++i) arr.push_back(dcp::out(x[i]));
  outputs = {{"x", arr}};
}
