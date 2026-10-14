// Four numbers: find three integers x1, x2, x3 between 1 and 10 such that every given number
// is the sum of some non-empty subset of {x1, x2, x3}.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> numbers = instance.at("numbers").get<std::vector<int>>();

  // x[i] is the i-th of the three integers, between 1 and 10 (the problem's range)
  vec<IntVar*> x;
  createVars(x, 3, 1, 10);

  // subset_sum[m-1] is the sum of the x[i] whose bit i is set in m, for each non-empty subset m = 1..7
  vec<IntVar*> subset_sum;
  for (int m = 1; m <= 7; ++m) {
    vec<int> coef;
    vec<IntVar*> chosen;
    for (int i = 0; i < 3; ++i) {
      if (m & (1 << i)) {
        coef.push(1);
        chosen.push(x[i]);
      }
    }
    IntVar* sum = newIntVar(1, 30);
    int_linear(coef, chosen, IRT_EQ, sum);
    subset_sum.push(sum);
  }

  // every given number is the sum of one of the subsets
  for (size_t k = 0; k < numbers.size(); ++k) {
    // hit[m-1] is true when subset m adds up to the given number
    vec<BoolView> hit;
    for (int m = 1; m <= 7; ++m) {
      BoolView b = newBoolVar();
      int_rel_reif(subset_sum[m - 1], IRT_EQ, numbers[k], b);
      hit.push(b);
    }
    bool_clause(hit);
  }

  // the three integers are the decision variables
  branch(x, VAR_INORDER, VAL_MIN);

  json triple = json::array();
  for (int i = 0; i < 3; ++i) triple.push_back(dcp::out(x[i]));
  outputs = {{"x", triple}};
}
