// n-queens, every solution: place n queens on an n x n board so that no two share
// a row, a column or a diagonal. q[i] is the column of the queen in row i.
// Usage: ./model [n]   (default 8)
#include <gecode/int.hh>
#include <gecode/minimodel.hh>
#include <gecode/search.hh>
#include <cstdlib>
#include <iostream>
using namespace Gecode;

class Queens : public Space {
 protected:
  IntVarArray q;

 public:
  explicit Queens(int n) : q(*this, n, 0, n - 1) {
    // one queen per column
    distinct(*this, q, IPL_DOM);
    // one queen per diagonal: q[i] + i and q[i] - i are all different
    IntArgs up(n), down(n);
    for (int i = 0; i < n; ++i) {
      up[i] = i;
      down[i] = -i;
    }
    distinct(*this, up, q, IPL_DOM);
    distinct(*this, down, q, IPL_DOM);
    branch(*this, q, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
  }
  Queens(Queens& s) : Space(s) { q.update(*this, s.q); }
  Space* copy() override { return new Queens(*this); }
  void print() const {
    for (int i = 0; i < q.size(); ++i) std::cout << q[i].val() << (i + 1 < q.size() ? " " : "\n");
  }
};

int main(int argc, char* argv[]) {
  int n = argc > 1 ? std::atoi(argv[1]) : 8;
  Queens* root = new Queens(n);
  DFS<Queens> engine(root);
  delete root;
  long count = 0;
  while (Queens* s = engine.next()) {  // each call returns the next solution
    if (count == 0) {
      std::cout << "First: ";
      s->print();
    }
    ++count;
    delete s;
  }
  // nullptr with stopped() == false means the search space is exhausted
  std::cout << "Solutions: " << count << (engine.stopped() ? " (stopped early)" : " (all)") << "\n";
  return 0;
}
