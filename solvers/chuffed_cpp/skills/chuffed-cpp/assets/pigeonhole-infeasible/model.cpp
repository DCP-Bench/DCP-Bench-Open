// Pigeonhole: put n + 1 pigeons into n holes, at most one pigeon per hole (infeasible).
//
// When the model already fails while it is posted or at the root, Chuffed prints
// "=====UNSATISFIABLE=====" and calls exit(0): engine.solve never returns and the code
// after it never runs (engine.status is not even updated). An atexit handler catches that.
// An infeasibility found later, by search, returns normally with 0 solutions.
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

static bool solve_returned = false;

class Pigeonhole : public Problem {
 public:
  vec<IntVar*> hole;  // hole[p] = the hole of pigeon p

  explicit Pigeonhole(int n) {
    createVars(hole, n + 1, 0, n - 1);
    // no two pigeons share a hole
    all_different(hole);
    branch(hole, VAR_INORDER, VAL_MIN);
  }

  void print(std::ostream& os) override {
    for (int i = 0; i < hole.size(); ++i) os << hole[i]->getVal() << ' ';
    os << "\n";
  }
};

int main() {
  std::atexit([] {
    if (!solve_returned) std::cout << "Infeasible: failed at the root, before search" << std::endl;
  });
  so.print_sol = true;
  engine.solve(new Pigeonhole(4));
  solve_returned = true;
  if (engine.solutions == 0 && engine.status != RES_UNK)
    std::cout << "Infeasible: proven by search" << std::endl;
  return 0;
}
