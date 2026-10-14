// Football: buy players with a total price as close as possible to GBP 30 million without going over, subject to squad rules.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // Data fixed by the problem statement. Prices in GBP thousands.
  const int budget = 30000;
  const int min_total_players = 11;
  const std::vector<int> goalkeepers = {730, 1280, 3880};
  const std::vector<int> defenders = {920, 1310, 1620, 2410, 2790, 3280, 3910, 4570};
  const std::vector<int> midfielders = {1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130};
  const std::vector<int> strikers = {4460, 6470, 7780, 8390, 9500};
  // each group: prices, minimum to buy, maximum to buy (-1 for no maximum)
  struct Group { const std::vector<int>* prices; int min_buy; int max_buy; };
  const Group groups[4] = {{&goalkeepers, 1, 1}, {&defenders, 2, -1}, {&midfielders, 3, -1}, {&strikers, 2, -1}};

  vec<IntVar*> bought;     // bought[p] = 1 if player p is bought
  vec<int> price;
  for (const Group& g : groups) {
    vec<IntVar*> in_group;
    vec<IntVar*> group_vars;
    for (int p : *g.prices) {
      IntVar* v = newIntVar(0, 1);
      bought.push(v);
      price.push(p);
      group_vars.push(v);
    }
    // the number of players bought from this group is within its limits
    // (goalkeepers: exactly 1; defenders at least 2; midfielders at least 3; strikers at least 2)
    int_linear(group_vars, IRT_GE, g.min_buy);
    if (g.max_buy >= 0) int_linear(group_vars, IRT_LE, g.max_buy);
  }

  // at least eleven players in total
  int_linear(bought, IRT_GE, min_total_players);

  // z is the total price of the chosen players; it must not exceed GBP 30 million
  IntVar* z = newIntVar(0, budget);
  int_linear(price, bought, IRT_EQ, z);

  // get as close to the budget as possible
  branch(bought, VAR_INORDER, VAL_MAX);
  optimize(z, OPT_MAX);
  outputs = {{"z", dcp::out(z)}};
}
