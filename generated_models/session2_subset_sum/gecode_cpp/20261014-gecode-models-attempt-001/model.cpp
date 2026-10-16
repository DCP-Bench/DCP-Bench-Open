// Subset sum for stolen coin bags: a bank van held several bags of coins, each
// bag type holding a given number of coins. Thieves stole some bags, losing a
// given total number of coins. Find how many bags were stolen of each type.
#include "dcp.h"

class SubsetSumBags : public dcp::Space {
 protected:
  IntVarArray bags;  // bags[i]: number of stolen bags of type i

 public:
  explicit SubsetSumBags(const json& instance) {
    std::vector<int> coins = instance.at("coin_numbers");
    int total = instance.at("total_coins_lost");
    int n = static_cast<int>(coins.size());

    // one count per bag type, from zero up to the total number of coins lost
    bags = IntVarArray(*this, n, 0, total);

    // a stolen bag of type i holds coins[i] coins, so at most total / coins[i]
    // bags of that type can have been stolen (the coin count is positive)
    for (int i = 0; i < n; ++i)
      rel(*this, bags[i], IRT_LQ, total / coins[i]);

    // the stolen bags together hold exactly the coins that were lost
    linear(*this, IntArgs(coins), bags, IRT_EQ, total);

    // branch on the bag counts, fewest first
    branch(*this, bags, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("bags", bags);
  }

  SubsetSumBags(SubsetSumBags& s) : dcp::Space(s) {
    bags.update(*this, s.bags);
  }
  Gecode::Space* copy() override { return new SubsetSumBags(*this); }
};

DCP_MODEL(SubsetSumBags)
