// Diet: choose whole numbers of four foods (chocolate cake, chocolate ice cream, cola,
// pineapple cheesecake) that meet the minimum calories, chocolate, sugar and fat
// requirements at the lowest total price.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> price = instance.at("price").get<std::vector<int>>();
  std::vector<int> limits = instance.at("limits").get<std::vector<int>>();
  int n = instance.at("n");

  // nutrient content per unit of each food (problem data, from the food table):
  // rows are calories, chocolate (ounces), sugar (ounces), fat (ounces);
  // columns are chocolate cake, chocolate ice cream, cola, pineapple cheesecake
  int content[4][4] = {
      {400, 200, 150, 500},
      {3, 2, 0, 0},
      {2, 2, 4, 4},
      {2, 4, 1, 5}};

  // amount[i] = number of units of food i bought (a generous upper bound)
  vec<IntVar*> amount;
  createVars(amount, n, 0, 1000);

  // every nutrient total must reach at least its requirement
  for (int k = 0; k < 4; ++k) {
    vec<int> coef;
    for (int i = 0; i < n; ++i) coef.push(content[k][i]);
    int_linear(coef, amount, IRT_GE, limits[k]);
  }

  // cost = total price of the units bought
  int max_cost = 0;
  for (int i = 0; i < n; ++i) max_cost += price[i] * 1000;
  IntVar* cost = newIntVar(0, max_cost);
  vec<int> pc;
  for (int i = 0; i < n; ++i) pc.push(price[i]);
  int_linear(pc, amount, IRT_EQ, cost);

  // minimize the cost of the diet
  branch(amount, VAR_INORDER, VAL_MIN);
  optimize(cost, OPT_MIN);

  outputs = {{"cost", dcp::out(cost)}};
}
