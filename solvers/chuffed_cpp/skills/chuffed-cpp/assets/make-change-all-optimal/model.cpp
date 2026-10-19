// Make change: pay an amount with as few coins as possible, then list every way to pay it
// with that minimum number of coins.
//
// Chuffed's solver state is process-wide and cannot be reset, so one process solves once.
// Phase 1 (minimise) runs in a fork()ed child that sends the optimum back through a pipe;
// phase 2 builds the model again in the parent with the objective fixed to the optimum and
// no optimize() call, and enumerates all solutions.
#include <chuffed/branching/branching.h>
#include <chuffed/core/engine.h>
#include <chuffed/core/options.h>
#include <chuffed/globals/globals.h>
#include <chuffed/primitives/primitives.h>
#include <chuffed/support/vec.h>
#include <chuffed/vars/int-var.h>
#include <chuffed/vars/modelling.h>

#include <sys/wait.h>
#include <unistd.h>

#include <iostream>
#include <ostream>
#include <vector>

class MakeChange : public Problem {
 public:
  vec<IntVar*> count;  // count[i] = number of coins of value coins[i]
  IntVar* total;       // number of coins used

  // fixed_total < 0: minimise the number of coins; otherwise fix it to that value
  MakeChange(int amount, const std::vector<int>& coins, int fixed_total) {
    int k = static_cast<int>(coins.size());
    createVars(count, k, 0, amount);

    // the coins add up to the amount
    vec<int> value;
    for (int c : coins) value.push(c);
    int_linear(value, count, IRT_EQ, amount);

    // total is the number of coins used
    total = newIntVar(0, amount);
    int_linear(count, IRT_EQ, total);

    branch(count, VAR_INORDER, VAL_MAX);
    if (fixed_total < 0) {
      optimize(total, OPT_MIN);
    } else {
      int_rel(total, IRT_EQ, fixed_total);
      output_vars(count);  // solutions differ in the coin counts
    }
  }

  void print(std::ostream& os) override {}  // output is done in the solution callback
};

// Phase 1 in a child process. Returns the optimum, or -1 when there is no solution.
int find_optimum(int amount, const std::vector<int>& coins) {
  int fd[2];
  if (pipe(fd) != 0) return -1;
  std::cout.flush();  // do not duplicate buffered output into the child
  pid_t pid = fork();
  if (pid == 0) {
    close(fd[0]);
    so.print_sol = false;
    engine.solve(new MakeChange(amount, coins, -1));
    // an optimisation search that did not time out has proven its last solution optimal
    if (engine.status != RES_UNK && engine.solutions > 0) {
      int best = engine.best_sol;
      if (write(fd[1], &best, sizeof best) != sizeof best) _exit(1);
    }
    _exit(0);  // a failure while posting calls exit(0) before this: nothing is written
  }
  close(fd[1]);
  int best = -1;
  if (read(fd[0], &best, sizeof best) != sizeof best) best = -1;
  close(fd[0]);
  waitpid(pid, nullptr, 0);
  return best;
}

int main() {
  int amount = 10;
  std::vector<int> coins = {2, 3, 4, 5, 6, 7};

  int best = find_optimum(amount, coins);
  if (best < 0) {
    std::cout << "No way to pay " << amount << std::endl;
    return 0;
  }
  std::cout << "Optimal coins: " << best << std::endl;

  // Phase 2 in this process: every solution with total == best
  so.nof_solutions = 0;  // 0 = all
  so.print_sol = false;
  engine.setSolutionCallback([&](Problem* p) {
    auto* m = static_cast<MakeChange*>(p);
    std::cout << "pay";
    for (int i = 0; i < m->count.size(); ++i)
      for (int j = 0; j < m->count[i]->getVal(); ++j) std::cout << ' ' << coins[i];
    std::cout << "\n";
  });
  engine.solve(new MakeChange(amount, coins, best));
  std::cout << "Optimal solutions: " << engine.solutions
            << (engine.status == RES_UNK ? " (time out, list incomplete)" : "") << std::endl;
  return 0;
}
