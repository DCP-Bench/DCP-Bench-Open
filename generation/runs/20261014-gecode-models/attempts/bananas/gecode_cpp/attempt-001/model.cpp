#include "dcp.h"

// Fruit purchase: buy 100 fruits (bananas, oranges, mangoes, apples) for exactly
// 100 dollars, buying at least one of each type, and minimise the quantities of
// bananas and apples.
class Bananas : public dcp::Space {
 protected:
  IntVarArray x;  // x[0] bananas, x[1] oranges, x[2] mangoes, x[3] apples
  IntVar cost;    // bananas + apples, the quantity to minimise

 public:
  explicit Bananas(const json& instance) {
    // all types of fruits need to be purchased: each quantity is at least 1
    x = IntVarArray(*this, 4, 1, 100);

    // 100 fruits in total
    linear(*this, IntArgs({1, 1, 1, 1}), x, IRT_EQ, 100);

    // 100 dollars in total. Prices are scaled by 315 (the lcm of 5, 7, 9 and 3)
    // so that they are integers: 5 bananas cost 3 dollars (189 each),
    // 7 oranges cost 5 dollars (225 each), 9 mangoes cost 7 dollars (245 each),
    // 3 apples cost 9 dollars (945 each). The budget is 100 dollars = 31500.
    linear(*this, IntArgs({189, 225, 245, 945}), x, IRT_EQ, 31500);

    // bananas and apples should be of minimum quantity
    cost = expr(*this, x[0] + x[3]);
    minimize(cost);

    branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("bananas", x[0]);
    output("oranges", x[1]);
    output("mangoes", x[2]);
    output("apples", x[3]);
  }

  Bananas(Bananas& s) : dcp::Space(s) {
    x.update(*this, s.x);
    cost.update(*this, s.cost);
  }
  Gecode::Space* copy() override { return new Bananas(*this); }
};

DCP_MODEL(Bananas)
