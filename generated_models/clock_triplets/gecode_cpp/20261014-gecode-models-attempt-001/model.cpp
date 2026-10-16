#include "dcp.h"

// Clock triplets: arrange the numbers 1 to 12 around the face of a clock so that
// no three adjacent numbers (going around the clock, so 11, 12, 1 is also a
// triplet) have a sum higher than 21.
//
// The clock size (12) and the sum limit (21) are fixed by the problem statement,
// so the instance carries no data for this model.
class ClockTriplets : public dcp::Space {
 protected:
  IntVarArray x;  // x[p]: number on clock position p (positions 0..11)

 public:
  explicit ClockTriplets(const json& /*instance*/) {
    const int n = 12;
    const int max_sum = 21;
    x = IntVarArray(*this, n, 1, n);

    // every number from 1 to 12 appears exactly once on the face
    distinct(*this, x, IPL_DOM);

    // no triplet of adjacent numbers has a sum higher than 21 (the clock wraps around)
    for (int p = 0; p < n; ++p) {
      IntVarArgs triplet;
      triplet << x[p] << x[(p + 1) % n] << x[(p + 2) % n];
      linear(*this, triplet, IRT_LQ, max_sum);
    }

    branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("x", x);
  }

  ClockTriplets(ClockTriplets& s) : dcp::Space(s) { x.update(*this, s.x); }
  Gecode::Space* copy() override { return new ClockTriplets(*this); }
};

DCP_MODEL(ClockTriplets)
