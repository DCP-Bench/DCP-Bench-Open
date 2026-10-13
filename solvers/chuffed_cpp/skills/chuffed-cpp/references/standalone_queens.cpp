// N-queens as a standalone Chuffed program: queens <n> [max_solutions]
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

  // Called for every solution; variables are fixed here and only here.
  void print(std::ostream& os) override {
    for (int i = 0; i < n; ++i) os << queens[i]->getVal() << (i + 1 < n ? " " : "\n");
  }
};

int main(int argc, char** argv) {
  if (argc < 2) {
    std::cerr << "usage: queens <n> [max_solutions]\n";
    return 2;
  }
  int n = std::atoi(argv[1]);
  so.nof_solutions = argc > 2 ? std::atoll(argv[2]) : 1;  // 0 means all
  so.print_sol = true;                                    // print() runs per solution
  engine.solve(new Queens(n));
  std::cout << "status " << (engine.status == RES_SAT ? "sat (stopped at limit)"
                             : engine.status == RES_UNK ? "unknown (time out)"
                                                        : "search complete")
            << ", solutions " << engine.solutions << std::endl;
  return 0;
}
