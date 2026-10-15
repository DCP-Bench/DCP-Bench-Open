#include "dcp.h"

// Circling the squares: place a different whole number in each of the ten squares
// of a ring (A B C D E F G H I K, in that order round the circle) so that for any two
// adjacent squares the sum of their squares equals the sum of the squares of the two
// diametrically opposite squares. Four numbers are given: A=16, B=2, F=8, G=14.
class CirclingSquares : public dcp::Space {
 protected:
  IntVarArray v;   // v[i]: the number in square i (0=A, 1=B, ..., 8=I, 9=K)
  IntVarArray sq;  // sq[i]: the square of v[i]

 public:
  explicit CirclingSquares(const json& instance) {
    (void)instance;  // the problem has no instance data: the given numbers are part of the statement

    // fractions are not allowed and no number needs more than two figures: whole numbers 0..99
    v = IntVarArray(*this, 10, 0, 99);
    sq = IntVarArray(*this, 10, 0, 99 * 99);

    // the square of each number
    for (int i = 0; i < 10; ++i) rel(*this, sq[i] == sqr(v[i]));

    // a different number in each of the ten squares
    distinct(*this, v, IPL_DOM);

    // the four numbers given in the statement: A=16, B=2, F=8, G=14
    rel(*this, v[0], IRT_EQ, 16);  // A
    rel(*this, v[1], IRT_EQ, 2);   // B
    rel(*this, v[5], IRT_EQ, 8);   // F
    rel(*this, v[6], IRT_EQ, 14);  // G

    // the squares of any two adjacent numbers sum to the squares of the two opposite
    // numbers; square i is opposite square i+5 on the ring, so the pair (i, i+1) is
    // opposite the pair (i+5, i+6). The equation for i+5 is the same one, so i=0..4 suffice.
    for (int i = 0; i < 5; ++i) {
      int j = (i + 1) % 10, k = (i + 5) % 10, l = (i + 6) % 10;
      rel(*this, sq[i] + sq[j] == sq[k] + sq[l]);
    }

    branch(*this, v, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("A", v[0]);
    output("B", v[1]);
    output("C", v[2]);
    output("D", v[3]);
    output("E", v[4]);
    output("F", v[5]);
    output("G", v[6]);
    output("H", v[7]);
    output("I", v[8]);
    output("K", v[9]);
  }

  CirclingSquares(CirclingSquares& s) : dcp::Space(s) {
    v.update(*this, s.v);
    sq.update(*this, s.sq);
  }
  Gecode::Space* copy() override { return new CirclingSquares(*this); }
};

DCP_MODEL(CirclingSquares)
