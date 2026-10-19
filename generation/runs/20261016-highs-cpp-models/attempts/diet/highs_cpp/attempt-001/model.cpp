// Diet problem: buy a whole number of units of each food so that the total meets at
// least the required amount of calories, chocolate, sugar and fat, at minimum cost.
// Output: cost, the price of the diet.
#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <vector>
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n").get<int>();
  if (n != 4) throw std::runtime_error("the food table has 4 foods");
  std::vector<double> price = instance.at("price").get<std::vector<double>>();
  std::vector<double> limits = instance.at("limits").get<std::vector<double>>();

  // Nutrition per unit of each food, from the description.
  // Rows: calories, chocolate (ounces), sugar (ounces), fat (ounces).
  // Columns: chocolate cake, chocolate ice cream, cola, pineapple cheesecake.
  const double amount[4][4] = {
      {400, 200, 150, 500},  // calories
      {3, 2, 0, 0},          // chocolate
      {2, 2, 4, 4},          // sugar
      {2, 4, 1, 5},          // fat
  };

  // Units of each food: whole numbers. Upper bound from the requirements: an optimal diet
  // never buys more of a food than the largest number of units that alone covers one of
  // the requirements it contributes to.
  std::vector<dcp::Lin> units;
  for (int j = 0; j < n; ++j) {
    int upper = 0;
    for (int i = 0; i < 4; ++i) {
      if (amount[i][j] > 0) {
        upper = std::max(upper, static_cast<int>(std::ceil(limits[i] / amount[i][j])));
      }
    }
    units.push_back(dcp::new_var(h, 0, upper));
  }

  // the diet supplies at least the required calories
  // the diet supplies at least the required chocolate
  // the diet supplies at least the required sugar
  // the diet supplies at least the required fat
  for (int i = 0; i < 4; ++i) {
    dcp::Lin total = 0.0;
    for (int j = 0; j < n; ++j) total = total + amount[i][j] * units[j];
    dcp::add_row(h, total, limits[i], kHighsInf);
  }

  // the cost is the price of each food times the units bought
  dcp::Lin cost = 0.0;
  for (int j = 0; j < n; ++j) cost = cost + price[j] * units[j];
  out.add("cost", cost);
  out.minimize(cost);
}
