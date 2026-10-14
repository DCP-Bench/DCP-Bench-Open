// Mario's gold collection: Mario starts at his house, visits a route of houses, returns to his house via Luigi's house, collects gold, and keeps the fuel used within the limit.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("nHouses");
  int mario = instance.at("marioHouse");
  int luigi = instance.at("luigiHouse");
  int fuel_limit = instance.at("fuelLimit");
  std::vector<std::vector<int>> arc_fuel = instance.at("arc_fuel").get<std::vector<std::vector<int>>>();
  std::vector<int> gold = instance.at("goldInHouse").get<std::vector<int>>();

  // succ[i] is the house visited after house i; succ[i] = i when house i is not on the route
  vec<IntVar*> succ;
  createVars(succ, n, 0, n - 1);

  // the houses on the route form one circuit; the others point to themselves
  subcircuit(succ, 0);

  // Luigi's house is followed by Mario's house, so Mario's route closes at Luigi's house
  int_rel(succ[luigi], IRT_EQ, mario);

  // Mario's house is on the route, so it does not point to itself
  int_rel(succ[mario], IRT_NE, mario);

  // fuel_cost[i] is the fuel used on the road from house i to the house after it (0 for houses not on the route)
  // flat is the fuel table indexed by from * n + to; the diagonal entries are 0 since no road leaves a house to itself
  vec<int> flat;
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) flat.push(i == j ? 0 : arc_fuel[i][j]);

  vec<IntVar*> fuel_cost;
  vec<int> one_coef;
  for (int i = 0; i < n; ++i) {
    // index = i * n + succ[i], the position of the road from i in the flat table
    IntVar* index = newIntVar(0, n * n - 1);
    vec<IntVar*> index_pair;
    index_pair.push(index); index_pair.push(succ[i]);
    vec<int> index_coef;
    index_coef.push(1); index_coef.push(-1);
    int_linear(index_coef, index_pair, IRT_EQ, i * n);
    IntVar* cost = newIntVar(0, 1000);
    array_int_element(index, flat, cost);
    fuel_cost.push(cost);
    one_coef.push(1);
  }

  // the total fuel used on the route must not exceed the fuel limit
  int_linear(one_coef, fuel_cost, IRT_LE, fuel_limit);

  // visited[i] is 1 when house i is on the route, and the gold collected is the gold of the visited houses
  vec<IntVar*> visited;
  vec<int> gold_coef;
  for (int i = 0; i < n; ++i) {
    BoolView on_route_is_false = newBoolVar();
    int_rel_reif(succ[i], IRT_EQ, i, on_route_is_false);
    BoolView on_route = ~on_route_is_false;
    IntVar* v = newIntVar(0, 1);
    bool2int(on_route, v);
    visited.push(v);
    gold_coef.push(gold[i]);
  }

  int total_gold = 0;
  for (int g : gold) total_gold += g;
  IntVar* collected = newIntVar(0, total_gold);
  int_linear(gold_coef, visited, IRT_EQ, collected);

  // maximize the gold collected; branch on the successors in house order
  vec<IntVar*> decisions;
  for (int i = 0; i < n; ++i) decisions.push(succ[i]);
  branch(decisions, VAR_INORDER, VAL_MIN);
  optimize(collected, OPT_MAX);

  json route = json::array();
  for (int i = 0; i < n; ++i) route.push_back(dcp::out(succ[i]));
  outputs = {{"s", route}};
}
