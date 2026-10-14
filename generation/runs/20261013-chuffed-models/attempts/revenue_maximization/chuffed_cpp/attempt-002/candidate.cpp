// Revenue maximization: choose how many units of each package to sell so that no flight leg's seats are
// overbooked and total revenue is maximal.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> seats = instance.at("available_seats").get<std::vector<int>>();
  std::vector<int> demand = instance.at("demand").get<std::vector<int>>();
  std::vector<int> revenue = instance.at("revenue").get<std::vector<int>>();
  std::vector<std::vector<int>> delta = instance.at("delta").get<std::vector<std::vector<int>>>();
  int packages = static_cast<int>(demand.size());
  int legs = static_cast<int>(seats.size());

  // sell[j] = units of package j sold, at most its estimated demand
  vec<IntVar*> sell;
  int max_revenue = 0;
  for (int j = 0; j < packages; ++j) {
    sell.push(newIntVar(0, demand[j]));
    max_revenue += revenue[j] * demand[j];
  }

  // every unit of a package reserves one seat on each leg the package uses,
  // so the seats reserved on a leg cannot exceed the seats available on it
  for (int l = 0; l < legs; ++l) {
    vec<int> coef;
    vec<IntVar*> vars;
    for (int j = 0; j < packages; ++j) {
      if (delta[j][l] != 0) {
        coef.push(delta[j][l]);
        vars.push(sell[j]);
      }
    }
    if (vars.size() > 0) int_linear(coef, vars, IRT_LE, seats[l]);
  }

  // the total revenue is the sum of the price of each package times the units sold
  vec<int> price;
  for (int j = 0; j < packages; ++j) price.push(revenue[j]);
  IntVar* total = newIntVar(0, max_revenue);
  int_linear(price, sell, IRT_EQ, total);
  optimize(total, OPT_MAX);

  branch(sell, VAR_INORDER, VAL_MAX);

  json units = json::array();
  for (int j = 0; j < packages; ++j) units.push_back(dcp::out(sell[j]));
  outputs = {{"packages_to_sell", units}, {"max_revenue", dcp::out(total)}};
}
