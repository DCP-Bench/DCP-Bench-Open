// Pigeonhole (infeasible): put n + 1 pigeons into n holes, one pigeon per hole.
// Shows the two ways Gecode proves infeasibility: the root space fails during
// propagation (status() == SS_FAILED), or the search ends with no solution and
// without being stopped.
#include <gecode/int.hh>
#include <gecode/minimodel.hh>
#include <gecode/search.hh>
#include <iostream>
using namespace Gecode;

class Pigeons : public Space {
 protected:
  IntVarArray hole;  // hole[p]: the hole of pigeon p

 public:
  Pigeons(int holes, IntPropLevel ipl) : hole(*this, holes + 1, 0, holes - 1) {
    // no two pigeons share a hole
    distinct(*this, hole, ipl);
    branch(*this, hole, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
  }
  Pigeons(Pigeons& s) : Space(s) { hole.update(*this, s.hole); }
  Space* copy() override { return new Pigeons(*this); }
};

void solve(const char* label, IntPropLevel ipl) {
  Pigeons* root = new Pigeons(3, ipl);
  if (root->status() == SS_FAILED) {  // propagation alone found the contradiction
    std::cout << label << ": no placement, root propagation failed\n";
    delete root;
    return;
  }
  DFS<Pigeons> engine(root);
  delete root;
  Search::Statistics st;
  if (Pigeons* s = engine.next()) {
    std::cout << label << ": found a placement\n";
    delete s;
  } else if (engine.stopped()) {
    std::cout << label << ": stopped before the search ended\n";
  } else {
    st = engine.statistics();
    std::cout << label << ": no placement, search exhausted after " << st.fail << " failures\n";
  }
}

int main() {
  solve("IPL_DOM", IPL_DOM);  // Hall-interval reasoning sees 4 pigeons in 3 holes at once
  solve("IPL_DEF", IPL_DEF);  // value propagation only: search must prove it
  return 0;
}
