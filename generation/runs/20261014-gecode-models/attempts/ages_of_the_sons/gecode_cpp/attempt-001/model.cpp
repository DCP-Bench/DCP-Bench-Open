#include "dcp.h"

// Ages of the three sons: find the ages a (oldest first) of three sons from the
// clues about their product, the sum, and the oldest son's unique identity.
class AgesOfTheSons : public dcp::Space {
 protected:
  IntVarArray a;  // a[0] >= a[1] >= a[2]: the three ages, oldest first
  IntVarArray b;  // b: a different triple with the same sum (witness for "need more information")

 public:
  // the instance has no fields: all sizes and constants come from the description
  explicit AgesOfTheSons(const json& instance) : a(*this, 3, 1, 36), b(*this, 3, 1, 36) {
    (void)instance;
    // the product of their ages is 36
    IntVar ab = expr(*this, a[0] * a[1], IPL_DOM);
    rel(*this, ab * a[2] == 36);

    // print the ages starting from the oldest
    rel(*this, a[0], IRT_GQ, a[1]);
    rel(*this, a[1], IRT_GQ, a[2]);

    // the sum of their ages equals the number of windows, which is not given
    IntVar sa = expr(*this, sum(a));

    // "I need more information" after the sum: another triple of ages with
    // product 36 has the same sum (witness b, sorted like a)
    IntVar bb = expr(*this, b[0] * b[1], IPL_DOM);
    rel(*this, bb * b[2] == 36);
    rel(*this, b[0], IRT_GQ, b[1]);
    rel(*this, b[1], IRT_GQ, b[2]);
    rel(*this, sum(b) == sa);

    // the witness is a different triple, not a reordering of a
    BoolVarArgs differs;
    for (int i = 0; i < 3; ++i) differs << expr(*this, a[i] != b[i]);
    linear(*this, differs, IRT_GQ, 1);

    // "the oldest son has blue eyes" and "I got it": the oldest age is unique
    rel(*this, a[0], IRT_GR, a[1]);

    output("A1", a[0]);
    output("A2", a[1]);
    output("A3", a[2]);

    branch(*this, a, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, b, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
  }

  AgesOfTheSons(AgesOfTheSons& s) : dcp::Space(s) {
    a.update(*this, s.a);
    b.update(*this, s.b);
  }
  Gecode::Space* copy() override { return new AgesOfTheSons(*this); }
};

DCP_MODEL(AgesOfTheSons)
