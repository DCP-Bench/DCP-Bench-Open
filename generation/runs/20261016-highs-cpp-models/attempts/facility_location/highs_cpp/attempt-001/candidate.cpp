// facility_location: open some of four candidate warehouse cities (New York, Los Angeles,
// Chicago, Atlanta) and ship every region's demand from the open warehouses, minimising
// the fixed opening costs plus the shipping costs.
#include <algorithm>

#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  std::vector<int> fixed_costs = instance.at("fixed_costs").get<std::vector<int>>();
  std::vector<int> demands = instance.at("demands").get<std::vector<int>>();
  std::vector<std::vector<int>> shipping_costs =
      instance.at("shipping_costs").get<std::vector<std::vector<int>>>();
  int max_shipping = instance.at("max_shipping").get<int>();

  const int warehouses = static_cast<int>(fixed_costs.size());  // 0 NY, 1 LA, 2 Chicago, 3 Atlanta
  const int regions = static_cast<int>(demands.size());

  // open[i] = 1 when warehouse i is operational
  std::vector<dcp::Lin> open;
  for (int i = 0; i < warehouses; i++) open.push_back(dcp::new_var(h, 0, 1));

  // ships[i][j] = units shipped from warehouse i to region j, at most the region's demand
  std::vector<std::vector<dcp::Lin>> ships(warehouses);
  for (int i = 0; i < warehouses; i++)
    for (int j = 0; j < regions; j++)
      ships[i].push_back(dcp::new_var(h, 0, std::min(max_shipping, demands[j])));

  // if the New York warehouse is opened, the Los Angeles warehouse must also be opened
  dcp::add_row(h, open[0] - open[1], -kHighsInf, 0);

  // no more than three warehouses can be operational
  dcp::Lin count;
  for (int i = 0; i < warehouses; i++) count = count + open[i];
  dcp::add_row(h, count, -kHighsInf, 3);

  // either the Atlanta or the Los Angeles warehouse must be opened
  dcp::add_row(h, open[3] + open[1], 1, kHighsInf);

  // an open warehouse ships at most max_shipping units in total; a closed one ships nothing
  for (int i = 0; i < warehouses; i++) {
    dcp::Lin shipped;
    for (int j = 0; j < regions; j++) shipped = shipped + ships[i][j];
    dcp::add_row(h, shipped - double(max_shipping) * open[i], -kHighsInf, 0);
  }

  // every region receives exactly its demand, from the open warehouses
  for (int j = 0; j < regions; j++) {
    dcp::Lin received;
    for (int i = 0; i < warehouses; i++) received = received + ships[i][j];
    dcp::add_row(h, received, demands[j], demands[j]);
  }

  // total cost: fixed opening costs of the open warehouses plus unit shipping costs
  dcp::Lin total_cost;
  for (int i = 0; i < warehouses; i++) {
    total_cost = total_cost + double(fixed_costs[i]) * open[i];
    for (int j = 0; j < regions; j++)
      total_cost = total_cost + double(shipping_costs[i][j]) * ships[i][j];
  }
  out.minimize(total_cost);

  out.add("open_warehouse", open);
  out.add("ships", ships);
  out.add("total_cost", total_cost);
}
