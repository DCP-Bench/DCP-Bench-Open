// Subset sum of bags: choose how many bags of each coin type were stolen so that the
// stolen bags contain exactly the total number of coins lost.
#include "dcp.h"

#include <vector>

void Build(const json& instance, json& outputs) {
  std::vector<int> coin_numbers = instance.at("coin_numbers").get<std::vector<int>>();  // coins per bag, by type
  int total = instance.at("total_coins_lost");
  int types = static_cast<int>(coin_numbers.size());

  // bags[i] is the number of stolen bags of type i; at most as many as fit in the total
  vec<IntVar*> bags;
  for (int i = 0; i < types; ++i) {
    IntVar* b = newIntVar(0, total / coin_numbers[i]);
    bags.push(b);
  }

  // the stolen bags hold exactly the total number of coins lost
  vec<int> coins;
  for (int i = 0; i < types; ++i) coins.push(coin_numbers[i]);
  int_linear(coins, bags, IRT_EQ, total);

  // branch on the bag counts in order, fewest bags first
  branch(bags, VAR_INORDER, VAL_MIN);

  json arr = json::array();
  for (int i = 0; i < types; ++i) arr.push_back(dcp::out(bags[i]));
  outputs = {{"bags", arr}};
}
