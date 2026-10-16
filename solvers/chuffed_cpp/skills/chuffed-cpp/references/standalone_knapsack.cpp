// 0/1 knapsack as a standalone Chuffed program with a hardcoded instance.
#include <chuffed/branching/branching.h>
#include <chuffed/core/engine.h>
#include <chuffed/core/options.h>
#include <chuffed/globals/globals.h>
#include <chuffed/primitives/primitives.h>
#include <chuffed/support/vec.h>
#include <chuffed/vars/int-var.h>
#include <chuffed/vars/modelling.h>

#include <chrono>
#include <iostream>
#include <ostream>
#include <vector>

class Knapsack : public Problem {
 public:
  int n;
  vec<IntVar*> take;
  IntVar* profit;

  Knapsack(const std::vector<int>& weights, const std::vector<int>& values, int capacity)
      : n(static_cast<int>(weights.size())) {
    // take[i] = 1 if item i goes into the knapsack
    createVars(take, n, 0, 1, true);

    vec<int> w, v;
    int total_value = 0;
    for (int i = 0; i < n; ++i) {
      w.push(weights[i]);
      v.push(values[i]);
      total_value += values[i];
    }

    // the total weight of the chosen items must not exceed the capacity
    int_linear(w, take, IRT_LE, capacity);

    // profit is the total value of the chosen items
    profit = newIntVar(0, total_value);
    int_linear(v, take, IRT_EQ, profit);

    // try taking items first, then maximize the profit
    branch(take, VAR_INORDER, VAL_MAX);
    optimize(profit, OPT_MAX);
  }

  // Called for each improving solution; the last one printed is the optimum.
  void print(std::ostream& os) override {
    os << "profit " << profit->getVal() << " take";
    for (int i = 0; i < n; ++i) os << ' ' << take[i]->getVal();
    os << "\n";
  }
};

int main() {
  std::vector<int> weights = {12, 7, 11, 8, 9};
  std::vector<int> values = {24, 13, 23, 15, 16};
  so.time_out = std::chrono::milliseconds(10000);
  so.print_sol = true;
  engine.solve(new Knapsack(weights, values, 26));
  std::cout << "status " << (engine.status == RES_UNK ? "unknown (time out)" : "search complete")
            << ", solutions " << engine.solutions << ", best objective " << engine.best_sol << std::endl;
  return 0;
}
