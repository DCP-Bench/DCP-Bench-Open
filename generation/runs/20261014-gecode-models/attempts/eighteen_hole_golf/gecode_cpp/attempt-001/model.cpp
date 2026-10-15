#include "dcp.h"

// Eighteen-hole golf course: choose a length of 3, 4 or 5 for each of the 18
// holes so that the total length of the course is 72.
class EighteenHoleGolf : public dcp::Space {
 protected:
  IntVarArray holes;  // holes[i]: length of hole i+1

 public:
  explicit EighteenHoleGolf(const json& instance) : holes(*this, 18, 3, 5) {
    (void)instance;  // the problem has no instance data

    // each hole has a length of 3, 4 or 5 (the domain of every variable)

    // the total length of the course is 72
    linear(*this, holes, IRT_EQ, 72);

    branch(*this, holes, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("holes", holes);
  }

  EighteenHoleGolf(EighteenHoleGolf& s) : dcp::Space(s) {
    holes.update(*this, s.holes);
  }
  Gecode::Space* copy() override { return new EighteenHoleGolf(*this); }
};

DCP_MODEL(EighteenHoleGolf)
