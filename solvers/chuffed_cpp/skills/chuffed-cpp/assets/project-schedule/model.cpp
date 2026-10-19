// Project scheduling: tasks with durations and worker demands, some tasks must finish before
// others start, at most `capacity` workers at any time; finish the project as early as possible.
#include <chuffed/branching/branching.h>
#include <chuffed/core/engine.h>
#include <chuffed/core/options.h>
#include <chuffed/globals/globals.h>
#include <chuffed/primitives/primitives.h>
#include <chuffed/support/vec.h>
#include <chuffed/vars/int-var.h>
#include <chuffed/vars/modelling.h>

#include <iostream>
#include <ostream>
#include <utility>
#include <vector>

class Project : public Problem {
 public:
  int n;
  vec<IntVar*> start;
  IntVar* makespan;

  Project(const std::vector<int>& duration, const std::vector<int>& demand, int capacity,
          const std::vector<std::pair<int, int>>& before)
      : n(static_cast<int>(duration.size())) {
    // the horizon: all tasks one after another
    int horizon = 0;
    for (int d : duration) horizon += d;

    createVars(start, n, 0, horizon);
    makespan = newIntVar(0, horizon);

    vec<int> d, r;
    for (int i = 0; i < n; ++i) {
      d.push(duration[i]);
      r.push(demand[i]);
    }

    // every task ends by the makespan: start[i] <= makespan - duration[i]
    for (int i = 0; i < n; ++i) int_rel(start[i], IRT_LE, makespan, -duration[i]);

    // task a finishes before task b starts: start[b] >= start[a] + duration[a]
    for (auto [a, b] : before) int_rel(start[b], IRT_GE, start[a], duration[a]);

    // at most `capacity` workers are busy at any time
    cumulative(start, d, r, capacity);

    // schedule the earliest-startable task first, at its earliest time
    branch(start, VAR_MIN_MIN, VAL_MIN);
    optimize(makespan, OPT_MIN);
  }

  void print(std::ostream& os) override {
    os << "makespan " << makespan->getVal() << " starts";
    for (int i = 0; i < n; ++i) os << ' ' << start[i]->getVal();
    os << "\n";
  }
};

int main() {
  std::vector<int> duration = {3, 2, 4, 2, 3, 1};
  std::vector<int> demand = {2, 1, 2, 1, 2, 3};
  int capacity = 3;
  std::vector<std::pair<int, int>> before = {{0, 2}, {1, 3}, {3, 4}, {2, 5}};

  so.print_sol = true;
  engine.solve(new Project(duration, demand, capacity, before));
  if (engine.status == RES_UNK)
    std::cout << "Time out, best makespan found " << engine.best_sol << std::endl;
  else if (engine.solutions == 0)
    std::cout << "Infeasible" << std::endl;
  else
    std::cout << "Optimal makespan: " << engine.best_sol << std::endl;
  return 0;
}
