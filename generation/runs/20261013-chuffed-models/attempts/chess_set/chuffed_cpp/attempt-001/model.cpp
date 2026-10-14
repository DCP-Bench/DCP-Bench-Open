// Chess sets: choose how many small and large boxwood chess sets to make to maximize profit.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // Data fixed by the problem statement (the instance file carries no fields).
  const int lathe_hours_small = 3, lathe_hours_large = 2;
  const int lathe_hours_available = 160;  // four lathes x 40 hours
  const int boxwood_small = 1, boxwood_large = 3;
  const int boxwood_available = 200;  // kg per week
  const int profit_small = 5, profit_large = 20;

  // number of small and large sets made each week (bounded by the lathe hours)
  IntVar* small_set = newIntVar(0, lathe_hours_available / lathe_hours_small);
  IntVar* large_set = newIntVar(0, lathe_hours_available / lathe_hours_large);
  vec<IntVar*> sets;
  sets.push(small_set);
  sets.push(large_set);

  // the lathe hours used must not exceed 160 hours per week
  vec<int> lathe;
  lathe.push(lathe_hours_small);
  lathe.push(lathe_hours_large);
  int_linear(lathe, sets, IRT_LE, lathe_hours_available);

  // the boxwood used must not exceed 200 kg per week
  vec<int> wood;
  wood.push(boxwood_small);
  wood.push(boxwood_large);
  int_linear(wood, sets, IRT_LE, boxwood_available);

  // max_profit is the total profit of the sets made (bounded by all hours spent on large sets)
  vec<int> prof;
  prof.push(profit_small);
  prof.push(profit_large);
  IntVar* max_profit = newIntVar(0, profit_small * 53 + profit_large * 80);
  int_linear(prof, sets, IRT_EQ, max_profit);

  // maximize the profit
  branch(sets, VAR_INORDER, VAL_MAX);
  optimize(max_profit, OPT_MAX);

  outputs = {{"small_set", dcp::out(small_set)},
             {"large_set", dcp::out(large_set)},
             {"max_profit", dcp::out(max_profit)}};
}
