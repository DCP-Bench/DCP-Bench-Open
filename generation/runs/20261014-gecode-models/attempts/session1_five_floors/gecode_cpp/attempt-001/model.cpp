#include "dcp.h"

// Five floors: Baker, Cooper, Fletcher, Miller and Smith each live on a different
// floor among the first five (floors 1 to 5), under the
// neighbour and position rules of the puzzle. Output: the floor of each person.
class FiveFloors : public dcp::Space {
 protected:
  IntVar B, C, F, M, S;

 public:
  explicit FiveFloors(const json& instance) : B(*this, 1, 5), C(*this, 1, 5), F(*this, 1, 5), M(*this, 1, 5), S(*this, 1, 5) {
    (void)instance;  // the puzzle has no instance data

    // the five people live on different floors
    IntVarArgs people;
    people << B << C << F << M << S;
    distinct(*this, people, IPL_DOM);

    // Baker does not live on the fifth floor
    rel(*this, B, IRT_NQ, 5);

    // Cooper does not live on the first floor
    rel(*this, C, IRT_NQ, 1);

    // Fletcher does not live on either the fifth or the first floor
    rel(*this, F, IRT_NQ, 5);
    rel(*this, F, IRT_NQ, 1);

    // Miller lives on a higher floor than Cooper
    rel(*this, M, IRT_GR, C);

    // Smith does not live on a floor adjacent to Fletcher
    rel(*this, S != F + 1);
    rel(*this, S != F - 1);

    // Fletcher does not live on a floor adjacent to Cooper
    rel(*this, F != C + 1);
    rel(*this, F != C - 1);

    // search over the people's floors in order
    branch(*this, people, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("B", B);
    output("C", C);
    output("F", F);
    output("M", M);
    output("S", S);
  }

  FiveFloors(FiveFloors& s) : dcp::Space(s) {
    B.update(*this, s.B);
    C.update(*this, s.C);
    F.update(*this, s.F);
    M.update(*this, s.M);
    S.update(*this, s.S);
  }
  Gecode::Space* copy() override { return new FiveFloors(*this); }
};

DCP_MODEL(FiveFloors)
