// csplib_034_warehouse_location: decide which warehouses to open from a set of candidate
// locations to supply a set of stores. Each warehouse has a fixed maintenance cost and a
// capacity limiting the number of stores it can supply. Each store must be supplied by
// exactly one open warehouse, at a supply cost that depends on the store and the warehouse.
// Minimise the sum of the maintenance costs of the opened warehouses and the supply costs.
// Outputs: total_cost, open_warehouses (binary per warehouse), supplier_assignment (per store,
// the 0-based warehouse index).
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int n_suppliers = instance.at("n_suppliers").get<int>();
  const int n_stores = instance.at("n_stores").get<int>();
  const double building_cost = instance.at("building_cost").get<double>();
  const std::vector<int> capacity = instance.at("capacity").get<std::vector<int>>();
  const std::vector<std::vector<int>> cost_matrix =
      instance.at("cost_matrix").get<std::vector<std::vector<int>>>();

  // open[w] = 1 when warehouse w is opened
  std::vector<dcp::Lin> open;
  for (int w = 0; w < n_suppliers; ++w) open.push_back(dcp::new_var(h, 0, 1));

  // supply[s][w] = 1 when store s is supplied by warehouse w
  std::vector<std::vector<dcp::Lin>> supply(n_stores, std::vector<dcp::Lin>(n_suppliers));
  for (int s = 0; s < n_stores; ++s)
    for (int w = 0; w < n_suppliers; ++w) supply[s][w] = dcp::new_var(h, 0, 1);

  // each store is supplied by exactly one warehouse
  for (int s = 0; s < n_stores; ++s) {
    dcp::Lin total;
    for (int w = 0; w < n_suppliers; ++w) total = total + supply[s][w];
    dcp::add_row(h, total, 1, 1);
  }

  // a store can only be supplied by a warehouse that is open
  for (int s = 0; s < n_stores; ++s)
    for (int w = 0; w < n_suppliers; ++w)
      dcp::add_row(h, supply[s][w] - open[w], -kHighsInf, 0);

  // a warehouse supplies at most its capacity of stores
  for (int w = 0; w < n_suppliers; ++w) {
    dcp::Lin load;
    for (int s = 0; s < n_stores; ++s) load = load + supply[s][w];
    dcp::add_row(h, load, -kHighsInf, capacity[w]);
  }

  // a warehouse is open only when it supplies at least one store
  for (int w = 0; w < n_suppliers; ++w) {
    dcp::Lin load;
    for (int s = 0; s < n_stores; ++s) load = load + supply[s][w];
    dcp::add_row(h, open[w] - load, -kHighsInf, 0);
  }

  // total cost: maintenance cost of the opened warehouses plus supply cost of the stores
  dcp::Lin total_cost;
  for (int w = 0; w < n_suppliers; ++w) total_cost = total_cost + building_cost * open[w];
  for (int s = 0; s < n_stores; ++s)
    for (int w = 0; w < n_suppliers; ++w)
      total_cost = total_cost + static_cast<double>(cost_matrix[s][w]) * supply[s][w];

  // supplier_assignment[s] = index of the warehouse that supplies store s (0-based)
  std::vector<dcp::Lin> supplier_assignment;
  for (int s = 0; s < n_stores; ++s) {
    dcp::Lin index;
    for (int w = 0; w < n_suppliers; ++w) index = index + static_cast<double>(w) * supply[s][w];
    supplier_assignment.push_back(index);
  }

  out.minimize(total_cost);
  out.add("total_cost", total_cost);
  out.add("open_warehouses", open);
  out.add("supplier_assignment", supplier_assignment);
}
