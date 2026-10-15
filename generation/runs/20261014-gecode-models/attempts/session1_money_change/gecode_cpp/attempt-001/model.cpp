#include "dcp.h"

// Money change: give Bob a change of the amount with the available coins,
// using as few coins as possible. coin_counts[i] is the number of coins of
// type i to give. Instance data: amount, types_of_coins (value of each type),
// available_coins (number of coins of each type that Alice has).
class MoneyChange : public dcp::Space {
 protected:
  IntVarArray coin_counts;  // coin_counts[i]: number of coins of type i given to Bob
  IntVar total;             // total number of coins given

 public:
  explicit MoneyChange(const json& instance) {
    int amount = instance.at("amount").get<int>();
    std::vector<int> values = instance.at("types_of_coins").get<std::vector<int>>();
    std::vector<int> available = instance.at("available_coins").get<std::vector<int>>();
    int n = static_cast<int>(values.size());

    int max_available = 0;
    for (int a : available) max_available = std::max(max_available, a);
    coin_counts = IntVarArray(*this, n, 0, max_available);

    // no more coins of a type than Alice has of that type
    for (int i = 0; i < n; ++i) rel(*this, coin_counts[i] <= available[i]);

    // the coins given add up to the amount
    linear(*this, IntArgs(values), coin_counts, IRT_EQ, amount, IPL_BND);

    // minimise the number of coins used
    total = expr(*this, sum(coin_counts));
    minimize(total);

    branch(*this, coin_counts, INT_VAR_SIZE_MIN(), INT_VAL_MAX());
    output("coin_counts", coin_counts);
  }

  MoneyChange(MoneyChange& s) : dcp::Space(s) {
    coin_counts.update(*this, s.coin_counts);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new MoneyChange(*this); }
};

DCP_MODEL(MoneyChange)
