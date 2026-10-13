// Facility location: choose which warehouses to open and how much each ships to each region, so that
// the regional demands are met at minimal total cost (fixed opening costs plus shipping costs).
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> demands = instance.at("demands").get<std::vector<int>>();
  std::vector<int> fixed_costs = instance.at("fixed_costs").get<std::vector<int>>();
  int max_shipping = instance.at("max_shipping");
  std::vector<std::vector<int>> shipping_costs = instance.at("shipping_costs").get<std::vector<std::vector<int>>>();
  int warehouses = static_cast<int>(fixed_costs.size());
  int regions = static_cast<int>(demands.size());
  // warehouse order in the instance: 0 = New York, 1 = Los Angeles, 2 = Chicago, 3 = Atlanta
  const int NEW_YORK = 0, LOS_ANGELES = 1, ATLANTA = 3;

  // open_warehouse[i] = 1 if warehouse i is opened
  vec<IntVar*> open_warehouse;
  createVars(open_warehouse, warehouses, 0, 1, true);

  // ships[i][j] = units shipped from warehouse i to region j (0 for warehouses that stay closed)
  vec<vec<IntVar*>> ships;
  for (int i = 0; i < warehouses; ++i) {
    ships.push();
    for (int j = 0; j < regions; ++j) {
      // a warehouse never ships more than max_shipping nor more than the region demands
      ships.last().push(newIntVar(0, std::min(max_shipping, demands[j])));
    }
  }

  // if the New York warehouse is opened, then the Los Angeles warehouse must also be opened
  int_rel(open_warehouse[NEW_YORK], IRT_LE, open_warehouse[LOS_ANGELES]);

  // no more than three warehouses can be operational
  int_linear(open_warehouse, IRT_LE, 3);

  // either the Atlanta or the Los Angeles warehouse must be opened
  bin_linear(open_warehouse[ATLANTA], open_warehouse[LOS_ANGELES], IRT_GE, 1);

  // a warehouse ships at most max_shipping units in total, and nothing when it is closed
  for (int i = 0; i < warehouses; ++i) {
    vec<int> coef;
    vec<IntVar*> terms;
    for (int j = 0; j < regions; ++j) {
      coef.push(1);
      terms.push(ships[i][j]);
    }
    coef.push(-max_shipping);
    terms.push(open_warehouse[i]);
    int_linear(coef, terms, IRT_LE, 0);
  }

  // the demand of every region must be met exactly
  for (int j = 0; j < regions; ++j) {
    vec<IntVar*> col;
    for (int i = 0; i < warehouses; ++i) col.push(ships[i][j]);
    int_linear(col, IRT_EQ, demands[j]);
  }

  // total cost = fixed costs of the opened warehouses + unit shipping costs of the shipments
  vec<int> coef;
  vec<IntVar*> terms;
  int bound = 0;
  for (int i = 0; i < warehouses; ++i) {
    coef.push(fixed_costs[i]);
    terms.push(open_warehouse[i]);
    bound += fixed_costs[i];
    int mx = 0;
    for (int j = 0; j < regions; ++j) {
      coef.push(shipping_costs[i][j]);
      terms.push(ships[i][j]);
      if (shipping_costs[i][j] > mx) mx = shipping_costs[i][j];
    }
    bound += mx * max_shipping;
  }
  IntVar* total_cost = newIntVar(0, bound);
  int_linear(coef, terms, IRT_EQ, total_cost);

  // decide which warehouses to open first, then the shipments
  vec<IntVar*> decisions;
  for (int i = 0; i < warehouses; ++i) decisions.push(open_warehouse[i]);
  for (int i = 0; i < warehouses; ++i)
    for (int j = 0; j < regions; ++j) decisions.push(ships[i][j]);
  branch(decisions, VAR_ACTIVITY, VAL_MIN);
  optimize(total_cost, OPT_MIN);

  json open = json::array(), ship = json::array();
  for (int i = 0; i < warehouses; ++i) {
    open.push_back(dcp::out(open_warehouse[i]));
    json row = json::array();
    for (int j = 0; j < regions; ++j) row.push_back(dcp::out(ships[i][j]));
    ship.push_back(row);
  }
  outputs = {{"open_warehouse", open}, {"ships", ship}, {"total_cost", dcp::out(total_cost)}};
}
