// Diet problem: buy whole units of each food so that every nutrient requirement
// is met at the lowest total cost, and report that cost.
#include "dcp.h"

#include <algorithm>
#include <stdexcept>

class Diet : public dcp::Space {
 protected:
  IntVarArray buy;  // buy[i]: units of food i bought
  IntVar cost;      // total price of the purchase

 public:
  explicit Diet(const json& instance) {
    int n = instance.at("n").get<int>();
    std::vector<int> price = instance.at("price").get<std::vector<int>>();
    std::vector<int> limits = instance.at("limits").get<std::vector<int>>();
    if (n != 4 || price.size() != 4 || limits.size() != 4)
      throw std::runtime_error("the diet table of the problem has four foods and four nutrients");
    for (int p : price)
      if (p < 0) throw std::runtime_error("food prices must not be negative");

    // Problem data, not instance data: nutrient content per unit of each food, in the
    // food order of the problem statement (chocolate cake, chocolate ice cream, cola,
    // pineapple cheesecake). Columns: calories, chocolate (ounces), sugar (ounces), fat (ounces).
    const std::vector<int> calories = {400, 200, 150, 500};
    const std::vector<int> chocolate = {3, 2, 0, 0};
    const std::vector<int> sugar = {2, 2, 4, 4};
    const std::vector<int> fat = {2, 4, 1, 5};

    // Upper bound on purchases of food i: the most units of it that any single
    // requirement needs, ceil(limit / content). Buying more than that adds cost
    // without satisfying anything new, because all contents and prices are
    // non-negative, so some optimal diet stays within these bounds.
    auto upper = [&](int i) {
      int ub = 0;
      const int content[4] = {calories[i], chocolate[i], sugar[i], fat[i]};
      for (int j = 0; j < 4; ++j)
        if (content[j] > 0)
          ub = std::max(ub, (limits[j] + content[j] - 1) / content[j]);
      return ub;
    };
    int max_ub = 0;
    std::vector<int> ub(n);
    for (int i = 0; i < n; ++i) {
      ub[i] = upper(i);
      max_ub = std::max(max_ub, ub[i]);
    }
    buy = IntVarArray(*this, n, 0, max_ub);
    for (int i = 0; i < n; ++i) rel(*this, buy[i] <= ub[i]);

    IntVarArgs units;
    for (int i = 0; i < n; ++i) units << buy[i];

    // the diet has at least limits[0] calories
    linear(*this, IntArgs(calories), units, IRT_GQ, limits[0], IPL_BND);

    // the diet has at least limits[1] ounces of chocolate
    linear(*this, IntArgs(chocolate), units, IRT_GQ, limits[1], IPL_BND);

    // the diet has at least limits[2] ounces of sugar
    linear(*this, IntArgs(sugar), units, IRT_GQ, limits[2], IPL_BND);

    // the diet has at least limits[3] ounces of fat
    linear(*this, IntArgs(fat), units, IRT_GQ, limits[3], IPL_BND);

    // the cost of the products: units bought times price, summed over the foods
    cost = expr(*this, sum(IntArgs(price), units));

    // branch on how many units of each food to buy
    branch(*this, buy, INT_VAR_SIZE_MIN(), INT_VAL_SPLIT_MIN());
    minimize(cost);
    output("cost", cost);
  }

  Diet(Diet& s) : dcp::Space(s) {
    buy.update(*this, s.buy);
    cost.update(*this, s.cost);
  }
  Gecode::Space* copy() override { return new Diet(*this); }
};

DCP_MODEL(Diet)
