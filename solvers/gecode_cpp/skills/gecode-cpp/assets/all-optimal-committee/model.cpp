// Cheapest committee, every optimal choice: choose 3 of 6 candidates with at least
// one from group A (0..2) and one from group B (3..5), at minimum total cost.
// Phase 1 proves the optimum with BAB; phase 2 fixes cost == optimum and enumerates
// every committee with DFS.
#include <gecode/int.hh>
#include <gecode/minimodel.hh>
#include <gecode/search.hh>
#include <iostream>
using namespace Gecode;

const int kCost[] = {2, 2, 3, 2, 4, 1};
const int kN = 6, kSize = 3;

class Committee : public IntMinimizeSpace {
 protected:
  BoolVarArray pick;
  IntVar total;

 public:
  // fixed_cost < 0: optimise; otherwise only committees of exactly that cost
  explicit Committee(int fixed_cost = -1) : pick(*this, kN, 0, 1), total(*this, 0, 100) {
    // exactly kSize members
    linear(*this, pick, IRT_EQ, kSize);
    // at least one from each group
    linear(*this, pick.slice(0, 1, 3), IRT_GQ, 1);
    linear(*this, pick.slice(3, 1, 3), IRT_GQ, 1);
    // total cost
    linear(*this, IntArgs(kN, kCost), pick, IRT_EQ, total);
    if (fixed_cost >= 0) rel(*this, total == fixed_cost);
    branch(*this, pick, BOOL_VAR_NONE(), BOOL_VAL_MAX());
  }
  Committee(Committee& s) : IntMinimizeSpace(s) {
    pick.update(*this, s.pick);
    total.update(*this, s.total);
  }
  Space* copy() override { return new Committee(*this); }
  IntVar cost() const override { return total; }  // what BAB minimises
  int value() const { return total.val(); }
  void print() const {
    std::cout << "  {";
    for (int i = 0, first = 1; i < kN; ++i)
      if (pick[i].val()) std::cout << (first ? "" : ", ") << i, first = 0;
    std::cout << "}\n";
  }
};

int main() {
  // Phase 1: branch and bound; every solution is better than the previous one,
  // so the last one is optimal once the search ends without being stopped.
  Committee* root = new Committee;
  BAB<Committee> bab(root);
  delete root;
  Committee* best = nullptr;
  while (Committee* s = bab.next()) {
    delete best;
    best = s;
  }
  if (best == nullptr || bab.stopped()) {
    std::cout << (best ? "Not proven optimal" : "No committee") << "\n";
    delete best;
    return 0;
  }
  int optimum = best->value();
  delete best;
  std::cout << "Optimal cost: " << optimum << "\n";

  // Phase 2: a fresh model with the cost fixed, enumerated with DFS
  Committee* fixed = new Committee(optimum);
  DFS<Committee> dfs(fixed);
  delete fixed;
  int count = 0;
  while (Committee* s = dfs.next()) {
    s->print();
    ++count;
    delete s;
  }
  std::cout << "Optimal choices: " << count << "\n";
  return 0;
}
