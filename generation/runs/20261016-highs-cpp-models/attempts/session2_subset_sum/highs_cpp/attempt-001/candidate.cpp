// Bank van subset sum: thieves stole some bags of coins. Each type of bag holds a
// given number of coins (coin_numbers), and the stolen bags hold a total of
// total_coins_lost coins. Find how many bags were stolen for each type of coin bag.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  std::vector<int> coins = instance.at("coin_numbers").get<std::vector<int>>();
  int total = instance.at("total_coins_lost").get<int>();

  // the number of bags stolen of each type, at most as many as fit in the total
  std::vector<dcp::Lin> bags;
  dcp::Lin lost = 0.0;
  for (size_t i = 0; i < coins.size(); ++i) {
    int upper = total / coins[i];
    bags.push_back(dcp::new_var(h, 0, upper));
    lost = lost + static_cast<double>(coins[i]) * bags[i];
  }

  // the stolen bags hold exactly total_coins_lost coins in all
  dcp::add_row(h, lost, total, total);

  out.add("bags", bags);
}
