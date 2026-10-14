// Diet: choose whole units of four foods so that the nutritional requirements are met
// at the lowest total cost.
#include "dcp.h"

#include <vector>

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");                                  // number of foods (4)
  std::vector<int> price = instance.at("price").get<std::vector<int>>();    // cents per unit
  std::vector<int> limits = instance.at("limits").get<std::vector<int>>();  // minimum calories, chocolate, sugar, fat

  // nutrient content per unit of each food, in the order cake, ice cream, cola, cheesecake
  // (problem data from the food table, not from the instance)
  std::vector<std::vector<int>> content = {
      {400, 200, 150, 500},  // calories
      {3, 2, 0, 0},          // chocolate (ounces)
      {2, 2, 4, 4},          // sugar (ounces)
      {2, 4, 1, 5},          // fat (ounces)
  };

  // units[i] is the number of units of food i bought; a generous bound, far above
  // any count the requirements in these instances can need
  vec<IntVar*> units;
  createVars(units, n, 0, 1000);

  // the diet must provide at least the required calories, chocolate, sugar and fat
  for (int j = 0; j < 4; ++j) {
    vec<int> coef;
    for (int i = 0; i < n; ++i) coef.push(content[j][i]);
    int_linear(coef, units, IRT_GE, limits[j]);
  }

  // cost is the total price of the units bought, in cents
  int max_price = 0;
  for (int i = 0; i < n; ++i) max_price += price[i];
  IntVar* cost = newIntVar(0, 1000 * max_price);
  vec<int> prices;
  for (int i = 0; i < n; ++i) prices.push(price[i]);
  int_linear(prices, units, IRT_EQ, cost);

  // try buying fewer units first, then minimize the cost
  branch(units, VAR_INORDER, VAL_MIN);
  optimize(cost, OPT_MIN);

  outputs = {{"cost", dcp::out(cost)}};
}
