// Revenue maximization: flight legs with limited passenger seats, and itinerary
// packages with a price and an estimated demand. Choose how many units of each
// package to sell so that the total revenue is maximal, while the seats reserved
// on every flight leg stay within its capacity.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const std::vector<int> seats = instance.at("available_seats").get<std::vector<int>>();
  const std::vector<int> demand = instance.at("demand").get<std::vector<int>>();
  const std::vector<int> revenue = instance.at("revenue").get<std::vector<int>>();
  const std::vector<std::vector<int>> delta = instance.at("delta").get<std::vector<std::vector<int>>>();

  const size_t num_legs = seats.size();
  const size_t num_packages = demand.size();

  // units of package p to sell: at most its estimated demand
  std::vector<dcp::Lin> sell;
  for (size_t p = 0; p < num_packages; ++p) {
    sell.push_back(dcp::new_var(h, 0, demand[p]));
  }

  // the seats reserved on each flight leg are at most the leg's passenger capacity:
  // each package sold reserves one seat on every leg it uses (delta[p][l] = 1)
  for (size_t l = 0; l < num_legs; ++l) {
    dcp::Lin reserved;
    for (size_t p = 0; p < num_packages; ++p) {
      if (delta[p][l] != 0) reserved = reserved + delta[p][l] * sell[p];
    }
    dcp::add_row(h, reserved, -kHighsInf, seats[l]);
  }

  // total revenue: the price of each package times the units sold
  dcp::Lin total;
  for (size_t p = 0; p < num_packages; ++p) {
    total = total + revenue[p] * sell[p];
  }
  out.maximize(total);

  out.add("max_revenue", total);
  out.add("packages_to_sell", sell);
}
