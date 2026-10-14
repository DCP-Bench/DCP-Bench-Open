#include "dcp.h"

// Minimum coins: choose how many coins of each denomination to hold so that every
// amount smaller than max_amount_to_pay can be paid exactly with those coins, and
// minimise the total number of coins.
class CoinsApplication : public dcp::Space {
 protected:
  IntVarArray x;     // x[i]: number of coins of denomination d[i]
  IntVar total;      // total number of coins
  std::vector<IntVarArray> pay;  // pay[a - 1][i]: coins of type i used to pay amount a

 public:
  explicit CoinsApplication(const json& instance) {
    std::vector<int> d = instance.at("denominations").get<std::vector<int>>();
    int max_amount = instance.at("max_amount_to_pay");
    int n = static_cast<int>(d.size());
    IntArgs denom(d);

    // a payment below max_amount uses at most (max_amount - 1) / d[i] coins of type i
    std::vector<int> cap(n);
    for (int i = 0; i < n; ++i) cap[i] = (max_amount - 1) / d[i];

    // x[i] is the number of coins of type i in the purse
    x = IntVarArray(*this, n, 0, 0);
    for (int i = 0; i < n; ++i) x[i] = IntVar(*this, 0, cap[i]);

    // every amount from 1 to max_amount - 1 can be paid exactly
    for (int a = 1; a < max_amount; ++a) {
      IntVarArray p(*this, n, 0, 0);
      for (int i = 0; i < n; ++i) {
        // a payment never uses more coins of one type than the amount allows
        p[i] = IntVar(*this, 0, std::min(a / d[i], cap[i]));
        // the payment only uses coins that are in the purse
        rel(*this, p[i], IRT_LQ, x[i]);
      }
      // the coins paid add up to exactly the amount
      linear(*this, denom, p, IRT_EQ, a);
      pay.push_back(p);
    }

    // the total number of coins is to be minimised
    total = expr(*this, sum(x));

    branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    for (auto& p : pay) branch(*this, p, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    minimize(total);
    output("x", x);
  }

  CoinsApplication(CoinsApplication& s) : dcp::Space(s) {
    x.update(*this, s.x);
    total.update(*this, s.total);
    pay.resize(s.pay.size());
    for (std::size_t a = 0; a < s.pay.size(); ++a) pay[a].update(*this, s.pay[a]);
  }
  Gecode::Space* copy() override { return new CoinsApplication(*this); }
};

DCP_MODEL(CoinsApplication)
