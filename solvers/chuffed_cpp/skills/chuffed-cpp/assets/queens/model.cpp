// N-queens: place n queens on an n x n board so that no two attack each other.
// Usage: model <n> [max_solutions]   (max_solutions 0 = all, default 1)
#include <chuffed/branching/branching.h>
#include <chuffed/core/engine.h>
#include <chuffed/core/options.h>
#include <chuffed/globals/globals.h>
#include <chuffed/primitives/primitives.h>
#include <chuffed/support/vec.h>
#include <chuffed/vars/int-var.h>
#include <chuffed/vars/modelling.h>

#include <cstdlib>
#include <iostream>
#include <ostream>

class Queens : public Problem {
 public:
  int n;
  vec<IntVar*> queens;

  explicit Queens(int n_) : n(n_) {
    // queens[i] is the row of the queen placed in column i
    createVars(queens, n, 0, n - 1);

    // no two queens share a row
    all_different(queens);

    // no two queens share a diagonal: queens[i] + i and queens[i] - i are all different
    vec<int> up, down;
    for (int i = 0; i < n; ++i) {
      up.push(i);
      down.push(-i);
    }
    all_different_offset(up, queens);
    all_different_offset(down, queens);

    // the queens are the decision variables; fill the emptiest column first
    branch(queens, VAR_SIZE_MIN, VAL_MIN);

    // solutions are told apart by these variables; needed to enumerate several
    output_vars(queens);
  }

  // Called for every solution when so.print_sol is true; variables are fixed here.
  void print(std::ostream& os) override {
    for (int i = 0; i < n; ++i) os << queens[i]->getVal() << (i + 1 < n ? " " : "\n");
  }
};

int main(int argc, char** argv) {
  if (argc < 2) {
    std::cerr << "usage: model <n> [max_solutions]\n";
    return 2;
  }
  int n = std::atoi(argv[1]);
  so.nof_solutions = argc > 2 ? std::atoll(argv[2]) : 1;  // 0 means all
  so.print_sol = true;                                    // print() runs per solution
  engine.solve(new Queens(n));

  // RES_SAT: stopped at the solution limit (more may exist); RES_GUN / RES_LUN: search
  // complete; RES_UNK: time out
  const char* status = engine.status == RES_SAT   ? "SAT (stopped at the solution limit)"
                       : engine.status == RES_UNK ? "UNKNOWN (time out)"
                                                  : "COMPLETE";
  std::cout << "n=" << n << " status " << status << ", solutions " << engine.solutions << std::endl;
  if (engine.solutions == 0 && engine.status != RES_UNK) std::cout << "No placement exists" << std::endl;
  return 0;
}
