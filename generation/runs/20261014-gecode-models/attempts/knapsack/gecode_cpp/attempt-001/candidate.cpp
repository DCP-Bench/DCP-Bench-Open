#include "dcp.h"

// 0-1 knapsack: a hiker chooses which items to put in a backpack so that the
// total value is maximised while the total weight stays within the capacity.
class Knapsack : public dcp::Space {
 protected:
  BoolVarArray take;  // take[i]: item i is in the backpack (True = taken)
  IntVar total;       // total value of the items in the backpack

 public:
  explicit Knapsack(const json& instance) {
    std::vector<int> values = instance.at("values");
    std::vector<int> weights = instance.at("weights");
    int capacity = instance.at("capacity");
    int n = static_cast<int>(values.size());

    take = BoolVarArray(*this, n, 0, 1);

    // the total weight of the chosen items must not exceed the capacity of the backpack
    linear(*this, IntArgs(weights), take, IRT_LQ, capacity, IPL_BND);

    // the total value of the chosen items is the quantity to maximise
    int value_sum = 0;
    for (int v : values) value_sum += v;
    total = IntVar(*this, 0, value_sum);
    linear(*this, IntArgs(values), take, IRT_EQ, total, IPL_BND);

    // decide each item in turn
    branch(*this, take, BOOL_VAR_NONE(), BOOL_VAL_MAX());

    // maximise the total value of the items in the backpack
    maximize(total);

    output("x", take);
  }

  Knapsack(Knapsack& s) : dcp::Space(s) {
    take.update(*this, s.take);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new Knapsack(*this); }
};

DCP_MODEL(Knapsack)
