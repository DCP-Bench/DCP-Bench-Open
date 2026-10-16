// Money change: pay an amount with the available coins using as few coins as possible.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int amount = instance.at("amount");
  std::vector<int> value = instance.at("types_of_coins").get<std::vector<int>>();
  std::vector<int> available = instance.at("available_coins").get<std::vector<int>>();
  int n = static_cast<int>(value.size());

  // coin_counts[i] is the number of coins of type i given to Bob, at most the number available
  vec<IntVar*> coin_counts;
  vec<int> v;
  int total_coins_max = 0;
  for (int i = 0; i < n; ++i) {
    int most = std::min(available[i], amount / value[i]);  // never more coins than fit in the amount
    coin_counts.push(newIntVar(0, most));
    v.push(value[i]);
    total_coins_max += most;
  }

  // the coins given must add up to the amount
  int_linear(v, coin_counts, IRT_EQ, amount);

  // minimize the number of coins used
  IntVar* n_coins = newIntVar(0, total_coins_max);
  int_linear(coin_counts, IRT_EQ, n_coins);
  branch(coin_counts, VAR_INORDER, VAL_MAX);
  optimize(n_coins, OPT_MIN);

  json out = json::array();
  for (int i = 0; i < n; ++i) out.push_back(dcp::out(coin_counts[i]));
  outputs = {{"coin_counts", out}};
}
