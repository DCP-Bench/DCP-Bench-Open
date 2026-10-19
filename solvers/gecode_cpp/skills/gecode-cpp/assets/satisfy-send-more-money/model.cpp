// SEND + MORE = MONEY: give each letter a different digit so the sum holds,
// with no leading zero. A satisfaction model searched with DFS.
#include <gecode/int.hh>
#include <gecode/minimodel.hh>
#include <gecode/search.hh>
#include <iostream>
using namespace Gecode;

class Money : public Space {
 protected:
  IntVarArray l;  // S E N D M O R Y

 public:
  Money() : l(*this, 8, 0, 9) {
    IntVar s(l[0]), e(l[1]), n(l[2]), d(l[3]), m(l[4]), o(l[5]), r(l[6]), y(l[7]);
    // no leading zero
    rel(*this, s != 0);
    rel(*this, m != 0);
    // every letter is a different digit
    distinct(*this, l, IPL_DOM);
    // the sum holds
    rel(*this, 1000 * s + 100 * e + 10 * n + d + 1000 * m + 100 * o + 10 * r + e ==
                   10000 * m + 1000 * o + 100 * n + 10 * e + y);
    branch(*this, l, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
  }
  Money(Money& other) : Space(other) { l.update(*this, other.l); }
  Space* copy() override { return new Money(*this); }

  int number(std::initializer_list<int> idx) const {
    int v = 0;
    for (int i : idx) v = 10 * v + l[i].val();
    return v;
  }
  void print() const {
    std::cout << number({0, 1, 2, 3}) << " + " << number({4, 5, 6, 1}) << " = "
              << number({4, 5, 2, 1, 7}) << "\n";
  }
};

int main() {
  Money* root = new Money;
  DFS<Money> engine(root);  // the engine searches its own clone of root
  delete root;
  if (Money* s = engine.next()) {
    s->print();
    delete s;
  } else if (engine.stopped()) {
    std::cout << "Stopped by a limit, no solution yet\n";
  } else {
    std::cout << "No solution\n";
  }
  return 0;
}
