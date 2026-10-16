// Project assignment problem. Each person i has Supply_i available hours and each
// project j requires Demand_j hours. The cost per hour of person i on project j is
// Cost_{i,j}, and person i can contribute to project j up to Limit_{i,j} hours.
// Minimise the total cost so that each person's hours sum to their supply and each
// project's hours sum to its demand. Output assign[i][j] (hours from person i to
// project j) and total_cost.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const auto& supply = instance.at("supply");
  const auto& demand = instance.at("demand");
  const auto& cost = instance.at("cost");
  const auto& limit = instance.at("limit");
  const int people = static_cast<int>(supply.size());
  const int projects = static_cast<int>(demand.size());

  // assign[i][j] is an integer number of hours from 0 up to Limit_{i,j}.
  std::vector<std::vector<dcp::Lin>> assign(people, std::vector<dcp::Lin>(projects));
  for (int i = 0; i < people; ++i)
    for (int j = 0; j < projects; ++j)
      assign[i][j] = dcp::new_var(h, 0, limit[i][j].get<double>());

  // the hours from each person i equal Supply_i
  for (int i = 0; i < people; ++i) {
    dcp::Lin row_sum;
    for (int j = 0; j < projects; ++j) row_sum = row_sum + assign[i][j];
    dcp::add_row(h, row_sum, supply[i].get<double>(), supply[i].get<double>());
  }

  // the hours assigned to each project j equal Demand_j
  for (int j = 0; j < projects; ++j) {
    dcp::Lin col_sum;
    for (int i = 0; i < people; ++i) col_sum = col_sum + assign[i][j];
    dcp::add_row(h, col_sum, demand[j].get<double>(), demand[j].get<double>());
  }

  // the total cost of all hours, to be minimised
  dcp::Lin total_cost;
  for (int i = 0; i < people; ++i)
    for (int j = 0; j < projects; ++j)
      total_cost = total_cost + cost[i][j].get<double>() * assign[i][j];

  out.add("assign", assign);
  out.add("total_cost", total_cost);
  out.minimize(total_cost);
}
