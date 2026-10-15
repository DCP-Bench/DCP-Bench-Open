#include "dcp.h"

// Frog on a circle of n cards. Cards 1..n are arranged clockwise on a circle;
// the frog starts on card 1 and from card k jumps k places clockwise. Find an
// arrangement such that the frog lands on every card.
class FrogCircle : public dcp::Space {
 protected:
  int n;
  IntVarArray x;     // x[i]: card at position i (positions 0..n-1 clockwise)
  IntVarArray succ;  // succ[i]: position the frog lands on after jumping from position i
  IntVarArray p;     // p[j]: position of the frog at its j-th jump (p[0] is the start)

 public:
  explicit FrogCircle(const json& instance) : n(instance.at("n").get<int>()) {
    x = IntVarArray(*this, n, 1, n);
    succ = IntVarArray(*this, n, 0, n - 1);
    p = IntVarArray(*this, n, 0, n - 1);

    // the cards are 1 to n, each used once
    distinct(*this, x, IPL_DOM);

    // rotating the whole arrangement gives the same circle, so card 1 is put at position 0,
    // where the frog starts
    rel(*this, x[0] == 1);
    rel(*this, p[0] == 0);

    // from card x[i] at position i the frog jumps x[i] places clockwise
    for (int i = 0; i < n; ++i) rel(*this, succ[i] == (x[i] + i) % n);

    // each jump goes from the position the frog is on to the next position it lands on
    for (int j = 0; j + 1 < n; ++j) element(*this, succ, p[j], p[j + 1]);

    // the frog lands on every card: its first n positions are all different
    distinct(*this, p, IPL_DOM);

    branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, succ, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, p, INT_VAR_NONE(), INT_VAL_MIN());
    output("x", x);
  }

  FrogCircle(FrogCircle& s) : dcp::Space(s), n(s.n) {
    x.update(*this, s.x);
    succ.update(*this, s.succ);
    p.update(*this, s.p);
  }
  Gecode::Space* copy() override { return new FrogCircle(*this); }
};

DCP_MODEL(FrogCircle)
