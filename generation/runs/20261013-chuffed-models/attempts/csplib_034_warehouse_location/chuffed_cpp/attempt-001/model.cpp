// Warehouse location: open warehouses and assign each store to one, minimizing building plus supply costs.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n_suppliers = instance.at("n_suppliers");  // candidate warehouses
  int n_stores = instance.at("n_stores");
  int building_cost = instance.at("building_cost");  // fixed maintenance cost of an open warehouse
  std::vector<int> capacity = instance.at("capacity").get<std::vector<int>>();
  std::vector<std::vector<int>> cost = instance.at("cost_matrix").get<std::vector<std::vector<int>>>();

  // supplier_assignment[s] is the warehouse supplying store s
  vec<IntVar*> supplier_assignment;
  createVars(supplier_assignment, n_stores, 0, n_suppliers - 1, true);

  // open_warehouses[w] = 1 if warehouse w is open; it is open exactly when it supplies a store
  vec<IntVar*> open_warehouses;
  createVars(open_warehouses, n_suppliers, 0, 1, true);

  // is_supplied[s][w] <-> store s is supplied by warehouse w
  vec<vec<BoolView>> is_supplied;
  createVars(is_supplied, n_stores, n_suppliers);
  for (int s = 0; s < n_stores; ++s)
    for (int w = 0; w < n_suppliers; ++w)
      int_rel_reif(supplier_assignment[s], IRT_EQ, w, is_supplied[s][w]);

  for (int w = 0; w < n_suppliers; ++w) {
    vec<BoolView> stores_of_w;
    for (int s = 0; s < n_stores; ++s) stores_of_w.push(is_supplied[s][w]);
    // a warehouse cannot supply more stores than its capacity
    IntVar* cap = getConstant(capacity[w]);
    bool_linear(stores_of_w, IRT_LE, cap);
    // each store is supplied by an open warehouse, and a warehouse supplying a store is open
    BoolView is_open = newBoolVar();
    bool2int(is_open, open_warehouses[w]);
    array_bool_or(stores_of_w, is_open);
  }

  // the supply cost of each store depends on its warehouse
  vec<IntVar*> supply_cost;
  int max_supply = 0;
  for (int s = 0; s < n_stores; ++s) {
    vec<int> row;
    int mx = 0;
    for (int w = 0; w < n_suppliers; ++w) {
      row.push(cost[s][w]);
      mx = std::max(mx, cost[s][w]);
    }
    max_supply += mx;
    IntVar* sc = newIntVar(0, mx);
    array_int_element(supplier_assignment[s], row, sc);
    supply_cost.push(sc);
  }

  // total cost = maintenance cost of the open warehouses + supply costs of all stores
  vec<int> coef;
  vec<IntVar*> terms;
  for (int w = 0; w < n_suppliers; ++w) {
    coef.push(building_cost);
    terms.push(open_warehouses[w]);
  }
  for (int s = 0; s < n_stores; ++s) {
    coef.push(1);
    terms.push(supply_cost[s]);
  }
  IntVar* total_cost = newIntVar(0, building_cost * n_suppliers + max_supply);
  int_linear(coef, terms, IRT_EQ, total_cost);

  branch(supplier_assignment, VAR_SIZE_MIN, VAL_MIN);
  optimize(total_cost, OPT_MIN);

  json open_out = json::array(), assign_out = json::array();
  for (int w = 0; w < n_suppliers; ++w) open_out.push_back(dcp::out(open_warehouses[w]));
  for (int s = 0; s < n_stores; ++s) assign_out.push_back(dcp::out(supplier_assignment[s]));
  outputs = {{"open_warehouses", open_out},
             {"supplier_assignment", assign_out},
             {"total_cost", dcp::out(total_cost)}};
}
