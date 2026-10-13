// Coin application: fewest coins such that every amount below the maximum amount can be paid exactly.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> denom = instance.at("denominations").get<std::vector<int>>();
  int max_amount = instance.at("max_amount_to_pay");
  int k = static_cast<int>(denom.size());

  // x[i] = number of coins of denomination i; more than (max_amount-1)/denom[i] of them can never be part
  // of a payment below max_amount, so the bound loses no optimal solution
  vec<IntVar*> x;
  int total_ub = 0;
  for (int i = 0; i < k; ++i) {
    int ub = (max_amount - 1) / denom[i];
    x.push(newIntVar(0, ub));
    total_ub += ub;
  }

  // every amount a from 1 to max_amount-1 must be payable: y[i] coins of denomination i pay exactly a,
  // and only coins that are in the purse can be used
  for (int a = 1; a < max_amount; ++a) {
    vec<IntVar*> y;
    vec<int> value;
    for (int i = 0; i < k; ++i) {
      IntVar* yi = newIntVar(0, a / denom[i]);
      int_rel(yi, IRT_LE, x[i], 0);
      y.push(yi);
      value.push(denom[i]);
    }
    // the coins used for amount a add up to a
    int_linear(value, y, IRT_EQ, a);
  }

  // the number of coins is the total number of coins in the purse
  IntVar* total = newIntVar(0, total_ub);
  int_linear(x, IRT_EQ, total);
  optimize(total, OPT_MIN);

  branch(x, VAR_INORDER, VAL_MIN);

  json counts = json::array();
  for (int i = 0; i < k; ++i) counts.push_back(dcp::out(x[i]));
  outputs = {{"x", counts}};
}
