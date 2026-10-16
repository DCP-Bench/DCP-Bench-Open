// Mario: Mario drives a route from his house to Luigi's house and back to his own.
// He collects the gold of every house on the route. The fuel of the drives must not
// exceed the fuel limit. Output s[i] is the house after house i (s[i] = i off the route).
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int n = instance.at("nHouses").get<int>();
  const int mario = instance.at("marioHouse").get<int>();
  const int luigi = instance.at("luigiHouse").get<int>();
  const double fuel_limit = instance.at("fuelLimit").get<double>();
  const json& arc_fuel = instance.at("arc_fuel");
  const json& gold = instance.at("goldInHouse");

  // house i is on the route (1) or not (0)
  std::vector<dcp::Lin> on(n);
  for (int i = 0; i < n; ++i) on[i] = dcp::new_var(h, 0, 1);

  // the route drives directly from house i to house j (1) or not (0), for i != j
  std::vector<std::vector<dcp::Lin>> drive(n, std::vector<dcp::Lin>(n));
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j)
      if (i != j) drive[i][j] = dcp::new_var(h, 0, 1);

  // position of house i along the route, counted from Mario's house (position 0)
  std::vector<dcp::Lin> pos(n);
  for (int i = 0; i < n; ++i) pos[i] = dcp::new_var(h, 0, n - 1, false);

  // Mario's house and Luigi's house are on the route
  dcp::add_row(h, on[mario], 1, 1);
  dcp::add_row(h, on[luigi], 1, 1);
  // Mario's house is the start of the route
  dcp::add_row(h, pos[mario], 0, 0);
  // Luigi's house is followed by Mario's house
  dcp::add_row(h, drive[luigi][mario], 1, 1);

  // each house on the route is left once, each house off the route is not left
  for (int i = 0; i < n; ++i) {
    dcp::Lin leaving;
    for (int j = 0; j < n; ++j)
      if (i != j) leaving = leaving + drive[i][j];
    dcp::add_row(h, leaving - on[i], 0, 0);
  }

  // each house on the route is entered once, each house off the route is not entered
  for (int j = 0; j < n; ++j) {
    dcp::Lin entering;
    for (int i = 0; i < n; ++i)
      if (i != j) entering = entering + drive[i][j];
    dcp::add_row(h, entering - on[j], 0, 0);
  }

  // the route is one loop through Mario's house, with no separate loops:
  // a drive into a house other than Mario's house moves the position up by one
  // (big-M = n - 1, the largest position difference)
  const double big_m = n - 1;
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j)
      if (i != j && j != mario)
        dcp::add_row(h, pos[j] - pos[i] - big_m * drive[i][j], 1 - big_m, kHighsInf);

  // the fuel of the drives stays within the fuel limit
  dcp::Lin fuel;
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j)
      if (i != j) fuel = fuel + arc_fuel.at(i).at(j).get<double>() * drive[i][j];
  dcp::add_row(h, fuel, -kHighsInf, fuel_limit);

  // the objective is the gold of the houses on the route, to be maximised
  dcp::Lin total_gold;
  for (int i = 0; i < n; ++i) total_gold = total_gold + gold.at(i).get<double>() * on[i];
  out.maximize(total_gold);

  // the succeeding house of i is i plus the sum of (j - i) over the drive from i to j,
  // so it is i when house i is not on the route
  std::vector<dcp::Lin> succ(n);
  for (int i = 0; i < n; ++i) {
    dcp::Lin s = dcp::Lin(static_cast<double>(i));
    for (int j = 0; j < n; ++j)
      if (i != j) s = s + static_cast<double>(j - i) * drive[i][j];
    succ[i] = s;
  }
  out.add("s", succ);
}
