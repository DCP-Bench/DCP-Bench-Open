#include "dcp.h"

// Pythagorean triplet: find three natural numbers a < b < c with
// a^2 + b^2 = c^2 and a + b + c = 1000. The description states there is
// exactly one such triplet; the ordering a < b < c is the usual convention
// that makes it unique (swapping a and b would otherwise give a second one).
class PythagoreanTriplet : public dcp::Space {
 protected:
  IntVar a, b, c;

 public:
  explicit PythagoreanTriplet(const json& instance) {
    (void)instance;  // the problem has no instance data; the sum 1000 is fixed by the description
    a = IntVar(*this, 1, 1000);
    b = IntVar(*this, 1, 1000);
    c = IntVar(*this, 1, 1000);

    // the three numbers are natural numbers in increasing order
    rel(*this, a < b);
    rel(*this, b < c);

    // a + b + c = 1000
    linear(*this, IntVarArgs({a, b, c}), IRT_EQ, 1000);

    // a^2 + b^2 = c^2
    rel(*this, a * a + b * b == c * c);

    // branch on the three numbers
    branch(*this, IntVarArgs({a, b, c}), INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("a", a);
    output("b", b);
    output("c", c);
  }

  PythagoreanTriplet(PythagoreanTriplet& s) : dcp::Space(s) {
    a.update(*this, s.a);
    b.update(*this, s.b);
    c.update(*this, s.c);
  }
  Gecode::Space* copy() override { return new PythagoreanTriplet(*this); }
};

DCP_MODEL(PythagoreanTriplet)
