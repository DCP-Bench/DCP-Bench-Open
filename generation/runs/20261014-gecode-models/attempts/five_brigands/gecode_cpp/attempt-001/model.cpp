#include "dcp.h"

// Five Spanish brigands (Alfonso A, Benito B, Carlos C, Diego D, Esteban E) count doubloons.
// Find how many doubloons each one has, so that the amounts satisfy the two conditions below.
class FiveBrigands : public dcp::Space {
 protected:
  IntVarArray x;  // x[0]=A, x[1]=B, x[2]=C, x[3]=D, x[4]=E (doubloons each)

 public:
  explicit FiveBrigands(const json& instance) : x(*this, 5, 1, 200) {
    (void)instance;  // the problem has no instance data; every number comes from the description
    IntVar A = x[0], B = x[1], C = x[2], D = x[3], E = x[4];

    // together they captured exactly 200 doubloons
    IntVarArgs total;
    for (int i = 0; i < 5; ++i) total << x[i];
    linear(*this, IntArgs({1, 1, 1, 1, 1}), total, IRT_EQ, 200);

    // with A twelve times, B three times, C the same, D half, E one-third, still 200 in all
    // (12A + 3B + C + D/2 + E/3 = 200, multiplied by 6 to avoid fractions)
    linear(*this, IntArgs({72, 18, 6, 3, 2}), total, IRT_EQ, 1200);

    // every brigand has at least one doubloon (domain lower bound 1 above)

    branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("A", A);
    output("B", B);
    output("C", C);
    output("D", D);
    output("E", E);
  }

  FiveBrigands(FiveBrigands& s) : dcp::Space(s) { x.update(*this, s.x); }
  Gecode::Space* copy() override { return new FiveBrigands(*this); }
};

DCP_MODEL(FiveBrigands)
