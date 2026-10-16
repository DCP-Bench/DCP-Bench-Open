// Multi-commodity transportation problem: ship every product from the origins to the
// destinations so that the total shipping cost is minimal, and print that cost as total_cost.
#include <algorithm>
#include <vector>

#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const auto& supply = instance.at("supply");  // supply[origin][product]
  const auto& demand = instance.at("demand");  // demand[destination][product]
  const auto& limit = instance.at("limit");    // limit[origin][destination]
  const auto& cost = instance.at("cost");      // cost[origin][destination][product]
  const int origins = static_cast<int>(supply.size());
  const int destinations = static_cast<int>(demand.size());
  const int products = static_cast<int>(supply[0].size());

  // ship[i][j][p]: units of product p sent from origin i to destination j
  std::vector<std::vector<std::vector<dcp::Lin>>> ship(
      origins, std::vector<std::vector<dcp::Lin>>(destinations, std::vector<dcp::Lin>(products)));
  for (int i = 0; i < origins; ++i) {
    for (int j = 0; j < destinations; ++j) {
      for (int p = 0; p < products; ++p) {
        // a shipment cannot exceed the origin's supply of that product or the lane limit
        int upper = std::min(supply[i][p].get<int>(), limit[i][j].get<int>());
        ship[i][j][p] = dcp::new_var(h, 0, upper);
      }
    }
  }

  // each origin ships no more of each product than its supply
  for (int i = 0; i < origins; ++i) {
    for (int p = 0; p < products; ++p) {
      dcp::Lin sent;
      for (int j = 0; j < destinations; ++j) sent = sent + ship[i][j][p];
      dcp::add_row(h, sent, -kHighsInf, supply[i][p].get<int>());
    }
  }

  // each destination receives exactly its demand of each product
  for (int j = 0; j < destinations; ++j) {
    for (int p = 0; p < products; ++p) {
      dcp::Lin received;
      for (int i = 0; i < origins; ++i) received = received + ship[i][j][p];
      int d = demand[j][p].get<int>();
      dcp::add_row(h, received, d, d);
    }
  }

  // the shipments on each origin-destination lane, all products together, stay within its limit
  for (int i = 0; i < origins; ++i) {
    for (int j = 0; j < destinations; ++j) {
      dcp::Lin lane;
      for (int p = 0; p < products; ++p) lane = lane + ship[i][j][p];
      dcp::add_row(h, lane, -kHighsInf, limit[i][j].get<int>());
    }
  }

  // the total shipping cost of all products over all lanes
  dcp::Lin total_cost;
  for (int i = 0; i < origins; ++i) {
    for (int j = 0; j < destinations; ++j) {
      for (int p = 0; p < products; ++p) {
        total_cost = total_cost + cost[i][j][p].get<double>() * ship[i][j][p];
      }
    }
  }
  out.add("total_cost", total_cost);
  out.minimize(total_cost);
}
