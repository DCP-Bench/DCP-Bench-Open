// Assign multiple aircraft types to routes. allocation[i][j] is the number of aircraft of
// type i assigned to route j. Each type i has availability[i] aircraft in total, each route j
// has passenger demand[j], and an aircraft of type i carries capabilities[i][j] passengers on
// route j at operational cost costs[i][j] per aircraft. Minimise the total cost.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const std::vector<int> availability = instance.at("availability").get<std::vector<int>>();
  const std::vector<int> demand = instance.at("demand").get<std::vector<int>>();
  const auto capabilities = instance.at("capabilities").get<std::vector<std::vector<int>>>();
  const auto costs = instance.at("costs").get<std::vector<std::vector<int>>>();
  const int types = static_cast<int>(availability.size());
  const int routes = static_cast<int>(demand.size());

  // allocation[i][j]: the number of aircraft of type i assigned to route j, at most availability[i]
  std::vector<std::vector<dcp::Lin>> allocation(types, std::vector<dcp::Lin>(routes));
  for (int i = 0; i < types; ++i)
    for (int j = 0; j < routes; ++j)
      allocation[i][j] = dcp::new_var(h, 0, availability[i]);

  // each type flies at most its availability in total
  for (int i = 0; i < types; ++i) {
    dcp::Lin used;
    for (int j = 0; j < routes; ++j) used = used + allocation[i][j];
    dcp::add_row(h, used, -kHighsInf, availability[i]);
  }

  // every route's passenger demand is met by the seats of the aircraft assigned to it
  for (int j = 0; j < routes; ++j) {
    dcp::Lin seats;
    for (int i = 0; i < types; ++i) seats = seats + capabilities[i][j] * allocation[i][j];
    dcp::add_row(h, seats, demand[j], kHighsInf);
  }

  // total operational cost is the objective
  dcp::Lin cost;
  for (int i = 0; i < types; ++i)
    for (int j = 0; j < routes; ++j) cost = cost + costs[i][j] * allocation[i][j];
  out.minimize(cost);

  out.add("allocation", allocation);
}
